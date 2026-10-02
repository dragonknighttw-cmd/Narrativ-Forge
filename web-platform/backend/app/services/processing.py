from __future__ import annotations

import json
import shutil
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
    job.progress = 0
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


def run_mock_job(job_id: str, db: Session) -> ProcessingJob:
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    if job.status == "completed":
        return job
    if job.status == "running":
        return job

    episode = db.get(Episode, job.episode_id)
    if not episode:
        return _fail(job, "EPISODE_NOT_FOUND", "Episode no longer exists", db)

    input_asset = db.get(Asset, job.input_asset_id) if job.input_asset_id else None
    if input_asset is None:
        input_asset = (
            db.query(Asset)
            .filter(Asset.episode_id == episode.id, Asset.status == "uploaded")
            .order_by(Asset.version.desc())
            .first()
        )
    if input_asset is None or not input_asset.local_path:
        return _fail(job, "INPUT_ASSET_MISSING", "Upload a source asset before processing", db)

    source = Path(input_asset.local_path)
    if not source.is_file():
        return _fail(job, "INPUT_FILE_MISSING", "The source file is not available", db)

    job.input_asset_id = input_asset.id
    job.status = "running"
    job.progress = 10
    if episode.status == "in_production":
        episode.status = "processing"
        episode.current_step = "processing"
    job.started_at = now()
    job.error_code = None
    job.error_message = None
    db.commit()

    try:
        output_dir = Path(settings.upload_dir) / episode.id / "processing"
        output_dir.mkdir(parents=True, exist_ok=True)

        preview_name = f"{uuid4().hex}_preview{source.suffix.lower() or '.bin'}"
        preview_path = output_dir / preview_name
        shutil.copyfile(source, preview_path)

        job.progress = 70
        db.commit()

        transcript = {
            "language": "my",
            "source": "mock",
            "segments": [
                {
                    "id": 1,
                    "start": 0.0,
                    "end": min(float(episode.target_duration_seconds), 3.0),
                    "text": "Mock transcript — replace with Whisper in the next integration phase.",
                }
            ],
        }
        transcript_path = output_dir / f"{uuid4().hex}_transcript.json"
        transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")

        version = (db.query(func.max(Asset.version)).filter(Asset.episode_id == episode.id).scalar() or 0) + 1
        output_asset = Asset(
            episode_id=episode.id,
            asset_type="processed_video" if input_asset.asset_type == "video" else "processed_media",
            original_filename=preview_name,
            storage_provider="local",
            local_path=str(preview_path),
            mime_type=input_asset.mime_type,
            file_size_bytes=preview_path.stat().st_size,
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
            storage_provider="local",
            local_path=str(transcript_path),
            mime_type="application/json",
            file_size_bytes=transcript_path.stat().st_size,
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
        job.duration_seconds = episode.target_duration_seconds
        job.completed_at = now()
        if episode.status == "processing":
            episode.status = "subtitle_review"
            episode.current_step = "subtitle"
        db.commit()
        db.refresh(job)
        return job
    except OSError as exc:
        return _fail(job, "PROCESSING_IO_ERROR", str(exc), db)
