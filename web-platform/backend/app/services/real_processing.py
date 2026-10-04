from __future__ import annotations

import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models import Asset, Episode, ProcessingJob
from .storage import StorageError, build_object_key, get_storage, materialize_asset
from .subtitles import generate_subtitle_for_episode


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


def _run(command: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout)


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

            _run(
                [
                    settings.whisper_command, str(source), "--language", "my", "--task", "transcribe",
                    "--output_format", "json", "--output_dir", str(transcript_dir), "--model", settings.whisper_model,
                ],
                timeout=settings.processing_timeout_seconds,
            )
            whisper_json = transcript_dir / f"{source.stem}.json"
            if not whisper_json.is_file():
                candidates = sorted(transcript_dir.glob("*.json"))
                if not candidates:
                    return _fail(job, "WHISPER_OUTPUT_MISSING", "Whisper completed without a JSON transcript", db)
                whisper_json = candidates[0]

            transcript = json.loads(whisper_json.read_text(encoding="utf-8"))
            transcript["source"] = "whisper"
            transcript["language"] = transcript.get("language", "my")
            transcript_path = work_dir / f"{uuid4().hex}_transcript.json"
            transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")

            version = (db.query(func.max(Asset.version)).filter(Asset.episode_id == episode.id).scalar() or 0) + 1
            output_key = build_object_key(episode.id, version, render_path.name, "processed_video")
            transcript_key = build_object_key(episode.id, version + 1, transcript_path.name, "transcript")
            storage = get_storage()
            stored_output = storage.upload_file(render_path, output_key, "video/mp4")
            stored_transcript = storage.upload_file(transcript_path, transcript_key, "application/json")

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
