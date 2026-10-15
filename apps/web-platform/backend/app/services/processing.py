from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import Asset, Episode, ProcessingJob, UploadSession
from .storage import StorageError, build_object_key, get_storage, materialize_asset


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

    input_asset = _source_asset(db, episode, job)
    if input_asset is None:
        return _fail(job, "INPUT_ASSET_MISSING", "Upload a source asset before processing", db)

    job.input_asset_id = input_asset.id
    job.status = "running"
    job.progress = 10
    if episode.status in {"idea", "planned", "script_draft", "script_review", "assets_needed", "in_production"}:
        episode.status = "processing"
        episode.current_step = "processing"
    job.started_at = now()
    job.error_code = None
    job.error_message = None
    db.commit()

    try:
        with tempfile.TemporaryDirectory(prefix="nf-mock-") as work:
            work_dir = Path(work)
            source = materialize_asset(input_asset, work_dir / "input")
            output_path = work_dir / f"{uuid4().hex}_preview{source.suffix.lower() or '.bin'}"
            output_path.write_bytes(source.read_bytes())

            job.progress = 70
            db.commit()

            transcript = {
                "language": "my",
                "source": "mock",
                "segments": [{
                    "id": 1,
                    "start": 0.0,
                    "end": min(float(episode.target_duration_seconds), 3.0),
                    "text": "နမူနာ မြန်မာ စာတန်းထိုး",
                }],
            }
            transcript_path = work_dir / f"{uuid4().hex}_transcript.json"
            transcript_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")

            db.query(Episode.id).filter(Episode.id == episode.id).with_for_update().first()
            asset_version = db.query(func.max(Asset.version)).filter(Asset.episode_id == episode.id).scalar() or 0
            reserved_version = db.query(func.max(UploadSession.reserved_version)).filter(
                UploadSession.episode_id == episode.id,
            ).scalar() or 0
            version = max(asset_version, reserved_version) + 1
            output_key = build_object_key(episode.id, version, output_path.name, "processed_video")
            transcript_key = build_object_key(episode.id, version + 1, transcript_path.name, "transcript")
            storage = get_storage()
            stored_output = storage.upload_file(output_path, output_key, input_asset.mime_type)
            stored_transcript = storage.upload_file(transcript_path, transcript_key, "application/json")

            output_asset = Asset(
                episode_id=episode.id,
                asset_type="processed_video" if input_asset.asset_type == "video" else "processed_media",
                original_filename=output_path.name,
                storage_provider=stored_output.provider,
                local_path=stored_output.local_path,
                object_key=stored_output.object_key,
                checksum_sha256=stored_output.checksum_sha256,
                mime_type=input_asset.mime_type,
                file_size_bytes=stored_output.size_bytes,
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
            job.duration_seconds = episode.target_duration_seconds
            job.completed_at = now()
            if episode.status == "processing":
                episode.status = "subtitle_review"
                episode.current_step = "subtitle"
            db.commit()
            db.refresh(job)
            return job
    except StorageError as exc:
        return _fail(job, "STORAGE_ERROR", str(exc), db)
    except OSError as exc:
        return _fail(job, "PROCESSING_IO_ERROR", str(exc), db)
