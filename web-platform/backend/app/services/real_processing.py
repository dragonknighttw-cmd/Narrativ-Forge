from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models import Asset, Episode, ProcessingJob, UploadSession
from .storage import StorageError, build_object_key, get_storage, materialize_asset, storage_provider_for_asset
from .subtitles import generate_subtitle_for_episode

logger = logging.getLogger(__name__)


def now() -> datetime:
    return datetime.now(timezone.utc)


def _fail(job: ProcessingJob, code: str, message: str, db: Session) -> ProcessingJob:
    job.status = "failed"
    job.error_code = code
    job.error_message = message
    job.last_error = message
    job.completed_at = now()
    episode = db.get(Episode, job.episode_id)
    if episode and episode.status in {"processing", "subtitle_review"}:
        episode.status = "failed"
        episode.current_step = "processing"
    db.commit()
    db.refresh(job)
    return job


def _posix_process_group_exists(process_group_id: int) -> bool:
    try:
        os.killpg(process_group_id, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _send_windows_tree_signal(process_id: int, *, force: bool) -> bool:
    command = ["taskkill", "/PID", str(process_id), "/T"]
    if force:
        command.append("/F")
    try:
        killer = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        killer.communicate()
    except OSError:
        logger.exception("Could not terminate Windows processing process tree pid=%s", process_id)
        return False
    if killer.returncode != 0:
        logger.warning(
            "Windows process-tree termination returned %s for pid=%s",
            killer.returncode,
            process_id,
        )
    return killer.returncode == 0


def _terminate_and_collect(
    process: subprocess.Popen[str],
    *,
    grace_seconds: float,
) -> tuple[str | None, str | None]:
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

        deadline = time.monotonic() + grace_seconds
        while _posix_process_group_exists(process.pid) and time.monotonic() < deadline:
            process.poll()
            time.sleep(min(0.05, max(0, deadline - time.monotonic())))

        if _posix_process_group_exists(process.pid):
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    else:
        try:
            process.send_signal(signal.CTRL_BREAK_EVENT)
        except (AttributeError, OSError):
            _send_windows_tree_signal(process.pid, force=False)

        _send_windows_tree_signal(process.pid, force=False)
        try:
            process.wait(timeout=grace_seconds)
        except subprocess.TimeoutExpired:
            pass
        _send_windows_tree_signal(process.pid, force=True)
        if process.poll() is None:
            try:
                process.kill()
            except OSError:
                logger.exception("Could not terminate Windows processing process pid=%s", process.pid)

    return process.communicate()


def _run(command: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
    process_options: dict[str, object] = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }
    if os.name == "posix":
        process_options["preexec_fn"] = os.setsid
    else:
        process_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    process = subprocess.Popen(command, **process_options)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        try:
            stdout, stderr = _terminate_and_collect(
                process,
                grace_seconds=settings.processing_timeout_grace_seconds,
            )
        except BaseException:
            logger.exception("Failed to fully clean up timed-out processing process pid=%s", process.pid)
            raise subprocess.TimeoutExpired(
                command,
                timeout,
                output=exc.output,
                stderr=exc.stderr,
            ) from exc
        raise subprocess.TimeoutExpired(
            command,
            timeout,
            output=stdout,
            stderr=stderr,
        ) from exc
    except BaseException:
        try:
            _terminate_and_collect(
                process,
                grace_seconds=settings.processing_timeout_grace_seconds,
            )
        except BaseException:
            logger.exception("Failed to clean up interrupted processing process pid=%s", process.pid)
        raise

    result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
    if process.returncode:
        raise subprocess.CalledProcessError(
            process.returncode,
            command,
            output=stdout,
            stderr=stderr,
        )
    return result


def _source_asset(db: Session, episode: Episode, job: ProcessingJob) -> Asset | None:
    if job.input_asset_id:
        asset = db.get(Asset, job.input_asset_id)
        if asset:
            return asset
    return (
        db.query(Asset)
        .filter(Asset.episode_id == episode.id, Asset.asset_type == "video", Asset.status == "uploaded")
        .order_by(Asset.version.desc())
        .first()
    )



def _validate_rendered_media(path: Path) -> tuple[int, int, float]:
    result = _run([
        settings.ffprobe_binary, "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ], timeout=settings.processing_timeout_seconds)
    data = json.loads(result.stdout or "{}")
    streams = data.get("streams", [])
    video = next((item for item in streams if item.get("codec_type") == "video"), None)
    audio = next((item for item in streams if item.get("codec_type") == "audio"), None)
    if not video:
        raise ValueError("Rendered output has no video stream")
    if not audio:
        raise ValueError("Rendered output has no audio stream")
    width, height = int(video.get("width", 0)), int(video.get("height", 0))
    if (width, height) != (1080, 1920):
        raise ValueError(f"Rendered output must be 1080x1920, got {width}x{height}")
    duration = float((data.get("format") or {}).get("duration") or 0)
    if duration <= 0:
        raise ValueError("Rendered output has invalid duration")
    return width, height, duration


def _transcribe_with_fallback(source: Path, transcript_dir: Path) -> Path:
    """Prefer configured Cloudflare Whisper, then fall back to local Whisper CLI."""
    remote_error: Exception | None = None
    if settings.whisper_remote_enabled and settings.cloudflare_whisper_worker_url:
        try:
            import requests

            with source.open("rb") as audio:
                response = requests.post(
                    settings.cloudflare_whisper_worker_url,
                    files={"file": (source.name, audio, "video/mp4")},
                    data={"language": "my", "task": "transcribe"},
                    headers=(
                        {"X-Whisper-Secret": settings.cloudflare_whisper_shared_secret}
                        if settings.cloudflare_whisper_shared_secret
                        else {}
                    ),
                    timeout=settings.whisper_remote_timeout_seconds,
                )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("Cloudflare Whisper returned a non-object response")
            payload["source"] = "cloudflare_whisper"
            payload["language"] = payload.get("language", "my")
            output = transcript_dir / f"{source.stem}.json"
            output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            return output
        except Exception as exc:
            remote_error = exc
            logger.warning(
                "cloudflare_whisper_failed_using_local_fallback",
                extra={"event": "whisper_fallback", "error_type": type(exc).__name__},
            )

    try:
        _run(
            [
                settings.whisper_command, str(source), "--language", "my", "--task", "transcribe",
                "--output_format", "json", "--output_dir", str(transcript_dir), "--model", settings.whisper_model,
            ],
            timeout=settings.processing_timeout_seconds,
        )
    except Exception:
        if remote_error is not None:
            logger.exception("local_whisper_fallback_failed", extra={"event": "whisper_fallback"})
        raise

    whisper_json = transcript_dir / f"{source.stem}.json"
    if not whisper_json.is_file():
        candidates = sorted(transcript_dir.glob("*.json"))
        if not candidates:
            if remote_error is not None:
                raise RuntimeError("Both Cloudflare Whisper and local Whisper fallback failed")
            raise RuntimeError("Whisper completed without a JSON transcript")
        whisper_json = candidates[0]
    return whisper_json

def run_real_job(job_id: str, db: Session, *, already_claimed: bool = False) -> ProcessingJob:
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    if job.status == "completed" or (job.status == "running" and not already_claimed):
        return job

    episode = db.get(Episode, job.episode_id)
    if not episode:
        return _fail(job, "EPISODE_NOT_FOUND", "Episode no longer exists", db)

    input_asset = _source_asset(db, episode, job)
    if not input_asset:
        return _fail(job, "INPUT_ASSET_MISSING", "Upload a source video before processing", db)

    job.input_asset_id = input_asset.id
    job.status = "running"
    job.progress = 5
    if not already_claimed:
        job.started_at = now()
    job.error_code = None
    job.error_message = None
    if episode.status == "in_production":
        episode.status = "processing"
        episode.current_step = "processing"
    db.commit()

    try:
        with tempfile.TemporaryDirectory(prefix="nf-real-") as work:
            work_dir = Path(work)
            source = materialize_asset(input_asset, work_dir / "input")
            render_path = work_dir / f"{uuid4().hex}_final.mp4"
            transcript_dir = work_dir / "whisper"
            transcript_dir.mkdir(parents=True, exist_ok=True)

            _run(
                [
                    settings.ffmpeg_binary, "-y", "-i", str(source),
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
                    "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                    "-c:a", "aac", "-ar", "48000", "-movflags", "+faststart", str(render_path),
                ],
                timeout=settings.processing_timeout_seconds,
            )
            width, height, duration = _validate_rendered_media(render_path)
            job.progress = 55
            db.commit()

            try:
                whisper_json = _transcribe_with_fallback(source, transcript_dir)
            except Exception as exc:
                return _fail(job, "WHISPER_OUTPUT_MISSING", str(exc), db)

            transcript = json.loads(whisper_json.read_text(encoding="utf-8"))
            transcript.setdefault("source", "whisper")
            transcript["language"] = transcript.get("language", "my")
            transcript_path = work_dir / f"{uuid4().hex}_transcript.json"
            transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")

            db.query(Episode.id).filter(Episode.id == episode.id).with_for_update().first()
            asset_version = db.query(func.max(Asset.version)).filter(Asset.episode_id == episode.id).scalar() or 0
            reserved_version = db.query(func.max(UploadSession.reserved_version)).filter(
                UploadSession.episode_id == episode.id,
            ).scalar() or 0
            version = max(asset_version, reserved_version) + 1
            output_key = build_object_key(episode.id, version, render_path.name, "processed_video")
            transcript_key = build_object_key(episode.id, version + 1, transcript_path.name, "transcript")
            output_provider = storage_provider_for_asset("video", render_path.stat().st_size, "video/mp4")
            transcript_provider = storage_provider_for_asset("transcript", transcript_path.stat().st_size, "application/json")
            stored_output = get_storage(output_provider).upload_file(render_path, output_key, "video/mp4")
            stored_transcript = get_storage(transcript_provider).upload_file(transcript_path, transcript_key, "application/json")

            output_asset = Asset(
                episode_id=episode.id,
                asset_type="processed_video",
                original_filename=render_path.name,
                storage_provider=stored_output.provider,
                local_path=stored_output.local_path,
                object_key=stored_output.object_key,
                checksum_sha256=stored_output.checksum_sha256,
                mime_type="video/mp4",
                file_size_bytes=stored_output.size_bytes,
                width=width,
                height=height,
                duration_seconds=round(duration),
                version=version,
                copyright_status=input_asset.copyright_status,
                status="processed",
                is_final=False,
            )
            db.add(output_asset)
            db.flush()

            transcript_asset = Asset(
                episode_id=episode.id,
                asset_type="transcript",
                original_filename=transcript_path.name,
                storage_provider=stored_transcript.provider,
                local_path=stored_transcript.local_path,
                object_key=stored_transcript.object_key,
                checksum_sha256=stored_transcript.checksum_sha256,
                mime_type="application/json",
                file_size_bytes=stored_transcript.size_bytes,
                version=version + 1,
                copyright_status="generated",
                status="completed",
                is_final=False,
            )
            db.add(transcript_asset)
            db.flush()

            job.output_asset_id = output_asset.id
            job.status = "completed"
            job.progress = 100
            job.duration_seconds = round(duration)
            episode.actual_duration_seconds = round(duration)
            job.completed_at = now()
            episode.status = "subtitle_review"
            episode.current_step = "subtitle"
            try:
                generate_subtitle_for_episode(db, episode.id, "burmese_default")
            except ValueError as exc:
                return _fail(job, "SUBTITLE_GENERATION_FAILED", str(exc), db)
            db.commit()
            db.refresh(job)
            return job
    except StorageError as exc:
        return _fail(job, "STORAGE_ERROR", str(exc), db)
    except subprocess.TimeoutExpired:
        return _fail(job, "PROCESSING_TIMEOUT", "Real media processing exceeded the configured timeout", db)
    except FileNotFoundError as exc:
        return _fail(job, "PROCESSING_TOOL_MISSING", f"Required processing tool is missing: {exc.filename}", db)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "Processing command failed").strip()
        return _fail(job, "PROCESSING_COMMAND_FAILED", detail[-2000:], db)
    except (OSError, json.JSONDecodeError) as exc:
        return _fail(job, "PROCESSING_IO_ERROR", str(exc), db)
