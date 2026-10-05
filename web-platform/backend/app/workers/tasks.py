from __future__ import annotations

import logging
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime, timedelta, timezone
from time import perf_counter
from typing import Optional

from sqlalchemy import and_, not_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import db as app_db
from ..core.config import settings
from .. import metrics
from ..models import Asset, FailedJob, ProcessingJob, StorageReplica
from ..services.audit import record_event
from ..services.asset_gc import purge_deleted_assets
from ..services.real_processing import run_real_job
from ..services.storage import StorageError, get_storage
from . import concurrency

logger = logging.getLogger(__name__)
INITIAL_RETRY_DELAY_SECONDS = 60
MAX_RETRY_DELAY_SECONDS = 3600


def _now() -> datetime:
    return datetime.now(timezone.utc)


def retry_delay_seconds(retry_number: int) -> int:
    if retry_number < 1:
        raise ValueError("retry_number must be at least 1")
    return min(INITIAL_RETRY_DELAY_SECONDS * (2 ** (retry_number - 1)), MAX_RETRY_DELAY_SECONDS)


def _claim_job(db: Session, job_id: str, claimed_at: datetime) -> bool:
    result = db.execute(
        update(ProcessingJob)
        .where(ProcessingJob.id == job_id, ProcessingJob.status == "queued")
        .values(
            status="running",
            progress=0,
            started_at=claimed_at,
            next_run_at=None,
            error_code=None,
            error_message=None,
            completed_at=None,
        )
    )
    db.commit()
    return result.rowcount == 1


def handle_attempt_failure(
    db: Session,
    job_id: str,
    claimed_at: datetime,
    reason: str,
) -> tuple[str, str | None]:
    """Atomically schedule a retry or persist an exhausted job and audit event."""
    db.rollback()
    state = db.execute(
        select(ProcessingJob.status, ProcessingJob.retry_count, ProcessingJob.max_retries).where(
            ProcessingJob.id == job_id,
            ProcessingJob.started_at == claimed_at,
            ProcessingJob.status.in_(("running", "failed")),
        )
    ).first()
    if state is None:
        return "superseded", None

    status, retry_count, max_retries = state
    now = _now()
    conditions = (
        ProcessingJob.id == job_id,
        ProcessingJob.status == status,
        ProcessingJob.retry_count == retry_count,
        ProcessingJob.started_at == claimed_at,
    )
    if retry_count < max_retries:
        due_at = now + timedelta(seconds=retry_delay_seconds(retry_count + 1))
        updated = db.execute(
            update(ProcessingJob)
            .where(*conditions, ProcessingJob.max_retries == max_retries)
            .values(
                status="queued",
                retry_count=ProcessingJob.retry_count + 1,
                next_run_at=due_at,
                last_error=reason,
                error_message=reason,
                completed_at=None,
                progress=0,
            )
        )
        if updated.rowcount != 1:
            db.rollback()
            return "superseded", None
        db.commit()
        return "scheduled", None

    active_failed_job = select(FailedJob.id).where(
        FailedJob.processing_job_id == job_id,
        FailedJob.resolved_at.is_(None),
    )
    updated = db.execute(
        update(ProcessingJob)
        .where(
            *conditions,
            ProcessingJob.max_retries == max_retries,
            ProcessingJob.retry_count >= ProcessingJob.max_retries,
            not_(active_failed_job.exists()),
        )
        .values(
            status="failed",
            next_run_at=None,
            last_error=reason,
            error_message=reason,
            completed_at=ProcessingJob.completed_at if status == "failed" else now,
        )
    )
    if updated.rowcount != 1:
        db.rollback()
        return "superseded", None

    failed_job = FailedJob(processing_job_id=job_id, reason=reason, retry_count=retry_count)
    db.add(failed_job)
    record_event(
        db,
        actor_email="system@narrativ.local",
        action="processing.retry_exhausted",
        resource_type="processing_job",
        resource_id=job_id,
        metadata={
            "processing_job_id": job_id,
            "retry_count": retry_count,
            "failure_reason": reason,
            "terminal_status": "failed",
        },
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return "superseded", None
    return "exhausted", failed_job.id


def publish_dead_letter(celery_app, db: Session, failed_job_id: str) -> bool:
    failed_job = db.get(FailedJob, failed_job_id)
    if failed_job is None or failed_job.resolved_at is not None or failed_job.dlq_published_at is not None:
        return False
    try:
        celery_app.send_task(
            "narrativ.dead_letter",
            args=[failed_job.processing_job_id],
            queue="dead_letter",
        )
    except Exception:
        logger.exception("Dead-letter queue publication failed for failed_job_id=%s", failed_job_id)
        return False

    result = db.execute(
        update(FailedJob)
        .where(
            FailedJob.id == failed_job_id,
            FailedJob.resolved_at.is_(None),
            FailedJob.dlq_published_at.is_(None),
        )
        .values(dlq_published_at=_now())
    )
    db.commit()
    return result.rowcount == 1


def enqueue_asset_replica(celery_app, asset_id: str) -> bool:
    if not settings.storage_replica_enabled or not settings.storage_replica_provider:
        return False
    try:
        celery_app.send_task("narrativ.replicate_asset", args=[asset_id])
        return True
    except Exception:
        logger.exception("storage_replica_enqueue_failed", extra={"asset_id": asset_id})
        return False


def register_tasks(celery_app):
    @celery_app.task(
        name="narrativ.replicate_asset",
        bind=True,
        autoretry_for=(StorageError,),
        retry_backoff=True,
        retry_backoff_max=3600,
        retry_kwargs={"max_retries": 5},
    )
    def replicate_asset_task(self, asset_id: str) -> str:
        db = app_db.SessionLocal()
        replica = None
        try:
            asset = db.get(Asset, asset_id)
            if asset is None:
                return asset_id
            provider = settings.storage_replica_provider.lower()
            if not provider or provider == asset.storage_provider.lower():
                return asset_id
            replica = db.query(StorageReplica).filter(
                StorageReplica.asset_id == asset.id,
                StorageReplica.provider == provider,
            ).first()
            if replica is None:
                replica = StorageReplica(
                    asset_id=asset.id,
                    provider=provider,
                    object_key=asset.object_key or f"episodes/{asset.episode_id}/assets/v{asset.version}/{asset.asset_type}/{asset.original_filename}",
                    status="queued",
                )
                db.add(replica)
                db.commit()
            if replica.status == "ready" and replica.checksum_sha256 == asset.checksum_sha256:
                return asset_id
            replica.status = "copying"
            replica.last_error = None
            replica.retry_count = self.request.retries
            db.commit()
            if not asset.object_key:
                raise StorageError("Primary asset object key is missing")
            source = get_storage(asset.storage_provider)
            destination = get_storage(provider)
            with tempfile.TemporaryDirectory(prefix="narrativ-replica-") as tmp:
                local_copy = Path(tmp) / Path(asset.original_filename).name
                source.download_file(asset.object_key, local_copy)
                stored = destination.upload_file(local_copy, replica.object_key, asset.mime_type)
            if asset.checksum_sha256 and stored.checksum_sha256 != asset.checksum_sha256:
                raise StorageError("Replica checksum does not match primary asset")
            replica.status = "ready"
            replica.checksum_sha256 = stored.checksum_sha256
            replica.size_bytes = stored.size_bytes
            replica.last_error = None
            replica.completed_at = _now()
            db.commit()
            return asset_id
        except Exception as exc:
            db.rollback()
            if replica is not None:
                try:
                    replica = db.get(StorageReplica, replica.id)
                    if replica:
                        replica.status = "failed"
                        replica.last_error = str(exc)[:4000]
                        replica.retry_count = self.request.retries
                        db.commit()
                except Exception:
                    db.rollback()
            if isinstance(exc, StorageError):
                raise
            raise StorageError("Asset replication failed") from exc
        finally:
            db.close()


    @celery_app.task(name="narrativ.process_real_job")
    def process_real_job_task(job_id: str) -> str:
        with concurrency.processing_semaphore.acquire():
            db: Optional[Session] = None
            try:
                db = app_db.SessionLocal()
                job = db.get(ProcessingJob, job_id)
                if not job:
                    raise RuntimeError("Processing job not found")
                if job.status in {"completed", "running", "failed"}:
                    return job.id

                claimed_at = _now()
                if not _claim_job(db, job_id, claimed_at):
                    return job_id

                metrics.record_processing_started()
                processing_started = perf_counter()
                processing_duration = 0.0
                processing_outcome = "failed"
                timed_out = False
                try:
                    try:
                        result = run_real_job(job_id, db, already_claimed=True)
                    finally:
                        processing_duration = perf_counter() - processing_started
                    timed_out = getattr(result, "error_code", None) == "PROCESSING_TIMEOUT"
                    if result.status == "failed":
                        reason = result.last_error or result.error_message or result.error_code or "Processing failed"
                        outcome, failed_job_id = handle_attempt_failure(db, job_id, claimed_at, reason)
                        processing_outcome = {
                            "scheduled": "retry",
                            "exhausted": "dlq",
                        }.get(outcome, "failed")
                    else:
                        outcome, failed_job_id = "completed", None
                        processing_outcome = "completed"
                        db.execute(
                            update(ProcessingJob)
                            .where(ProcessingJob.id == job_id, ProcessingJob.status == "completed")
                            .values(last_error=None, next_run_at=None)
                        )
                        db.commit()
                except Exception as exc:
                    timed_out = timed_out or isinstance(exc, subprocess.TimeoutExpired)
                    outcome, failed_job_id = handle_attempt_failure(db, job_id, claimed_at, str(exc))
                    processing_outcome = {
                        "scheduled": "retry",
                        "exhausted": "dlq",
                    }.get(outcome, "failed")
                finally:
                    metrics.record_processing_finished(
                        processing_outcome,
                        processing_duration,
                        timed_out=timed_out,
                    )

                if outcome == "exhausted" and failed_job_id is not None:
                    publish_dead_letter(celery_app, db, failed_job_id)
                return job_id
            finally:
                if db is not None:
                    db.close()



    @celery_app.task(name="narrativ.purge_deleted_assets")
    def purge_deleted_assets_task():
        db = app_db.SessionLocal()
        try:
            return purge_deleted_assets(db)
        finally:
            db.close()

    @celery_app.task(name="narrativ.dead_letter")
    def dead_letter_notification_task(job_id: str) -> str:
        logger.error("Processing job entered dead-letter queue: job_id=%s", job_id)
        return job_id

    return process_real_job_task
