from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import and_, not_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import db as app_db
from ..models import FailedJob, ProcessingJob
from ..services.audit import record_event
from ..services.real_processing import run_real_job

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


def register_tasks(celery_app):
    @celery_app.task(name="narrativ.process_real_job")
    def process_real_job_task(job_id: str) -> str:
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

            try:
                result = run_real_job(job_id, db, already_claimed=True)
                if result.status == "failed":
                    reason = result.last_error or result.error_message or result.error_code or "Processing failed"
                    outcome, failed_job_id = handle_attempt_failure(db, job_id, claimed_at, reason)
                else:
                    outcome, failed_job_id = "completed", None
                    db.execute(
                        update(ProcessingJob)
                        .where(ProcessingJob.id == job_id, ProcessingJob.status == "completed")
                        .values(last_error=None, next_run_at=None)
                    )
                    db.commit()
            except Exception as exc:
                outcome, failed_job_id = handle_attempt_failure(db, job_id, claimed_at, str(exc))

            if outcome == "exhausted" and failed_job_id is not None:
                publish_dead_letter(celery_app, db, failed_job_id)
            return job_id
        finally:
            if db is not None:
                db.close()

    @celery_app.task(name="narrativ.dead_letter")
    def dead_letter_notification_task(job_id: str) -> str:
        logger.error("Processing job entered dead-letter queue: job_id=%s", job_id)
        return job_id

    return process_real_job_task
