from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models import Asset, Episode, ProcessingJob


def now() -> datetime:
    return datetime.now(timezone.utc)


def _fail(job: ProcessingJob, code: str, message: str, db: Session) -> ProcessingJob:
    job.status = "failed"
    job.error_code = code
    job.error_message = message
    job.completed_at = now()
    episode = db.get(Episode, job.episode_id)
    if episode and episode.status == "processing":
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


def run_real_job(job_id: str, db: Session) -> ProcessingJob:
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    if job.status in {"completed", "running"}:
        return job

    episode = db.get(Episode, job.episode_id)
    if not episode:
        return _fail(job, "EPISODE_NOT_FOUND", "Episode no longer exists", db)

    input_asset = _source_asset(db, episode, job)
    if not input_asset or not input_asset.local_path:
        return _fail(job, "INPUT_ASSET_MISSING", "Upload a source video before processing", db)

    source = Path(input_asset.local_path)
    if not source.is_file():
        return _fail(job, "INPUT_FILE_MISSING", "The source file is not available", db)

    output_dir = Path(settings.upload_dir) / episode.id / "processing"
    output_dir.mkdir(parents=True, exist_ok=True)
    render_path = output_dir / f"{uuid4().hex}_final.mp4"
    transcript_dir = output_dir / f"{uuid4().hex}_whisper"
    transcript_dir.mkdir(parents=True, exist_ok=True)

    job.input_asset_id = input_asset.id
    job.status = "running"
    job.progress = 5
    job.started_at = now()
    job.error_code = None
    job.error_message = None
    if episode.status == "in_production":
        episode.status = "processing"
        episode.current_step = "processing"
    db.commit()

    try:
        _run(
            [
                settings.ffmpeg_binary, "-y", "-i", str(source),
                "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1",
                "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "23",
                "-c:a", "aac", "-ar", "48000", "-movflags", "+faststart", str(render_path),
            ],
            timeout=settings.processing_timeout_seconds,
        )
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
        transcript_path = output_dir / f"{uuid4().hex}_transcript.json"
        transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")

        version = (db.query(func.max(Asset.version)).filter(Asset.episode_id == episode.id).scalar() or 0) + 1
        output_asset = Asset(
            episode_id=episode.id, asset_type="processed_video", original_filename=render_path.name,
            storage_provider="local", local_path=str(render_path), mime_type="video/mp4",
            file_size_bytes=render_path.stat().st_size, version=version,
            copyright_status=input_asset.copyright_status, status="processed", is_final=False,
        )
        db.add(output_asset)
        db.flush()

        transcript_asset = Asset(
            episode_id=episode.id, asset_type="transcript", original_filename=transcript_path.name,
            storage_provider="local", local_path=str(transcript_path), mime_type="application/json",
            file_size_bytes=transcript_path.stat().st_size, version=version + 1,
            copyright_status="generated", status="completed", is_final=False,
        )
        db.add(transcript_asset)
        db.flush()

        job.output_asset_id = output_asset.id
        job.status = "completed"
        job.progress = 100
        job.duration_seconds = episode.target_duration_seconds
        job.completed_at = now()
        episode.status = "subtitle_review"
        episode.current_step = "subtitle"
        db.commit()
        db.refresh(job)
        return job
    except subprocess.TimeoutExpired:
        return _fail(job, "PROCESSING_TIMEOUT", "Real media processing exceeded the configured timeout", db)
    except FileNotFoundError as exc:
        return _fail(job, "PROCESSING_TOOL_MISSING", f"Required processing tool is missing: {exc.filename}", db)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "Processing command failed").strip()
        return _fail(job, "PROCESSING_COMMAND_FAILED", detail[-2000:], db)
    except (OSError, json.JSONDecodeError) as exc:
        return _fail(job, "PROCESSING_IO_ERROR", str(exc), db)
