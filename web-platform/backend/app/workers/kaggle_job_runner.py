from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import or_, update

from ..db import SessionLocal
from ..models import ProcessingJob
from ..services.real_processing import run_real_job
from .tasks import handle_attempt_failure

logger = logging.getLogger(__name__)

def _now() -> datetime:
    return datetime.now(timezone.utc)

def claim_next_job() -> tuple[str, datetime] | None:
    db = SessionLocal()
    try:
        now = _now()
        job = (
            db.query(ProcessingJob)
            .filter(
                ProcessingJob.job_type == "real_processing",
                ProcessingJob.status == "queued",
                or_(ProcessingJob.next_run_at.is_(None), ProcessingJob.next_run_at <= now),
            )
            .order_by(ProcessingJob.created_at.asc())
            .first()
        )
        if job is None:
            return None
        claimed_at = now
        updated = db.execute(
            update(ProcessingJob)
            .where(ProcessingJob.id == job.id, ProcessingJob.status == "queued")
            .values(status="running", progress=0, started_at=claimed_at, next_run_at=None, error_code=None, error_message=None, completed_at=None)
        )
        db.commit()
        if updated.rowcount != 1:
            return None
        return job.id, claimed_at
    finally:
        db.close()

def run_one_job() -> str:
    claimed = claim_next_job()
    if claimed is None:
        logger.info("No queued real-processing job available")
        return "empty"
    job_id, claimed_at = claimed
    db = SessionLocal()
    try:
        result = run_real_job(job_id, db, already_claimed=True)
        if result.status == "failed":
            reason = result.last_error or result.error_message or result.error_code or "Processing failed"
            outcome, _ = handle_attempt_failure(db, job_id, claimed_at, reason)
            logger.info("Kaggle job %s finished with outcome=%s", job_id, outcome)
            return outcome
        logger.info("Kaggle job %s completed", job_id)
        return "completed"
    except Exception as exc:
        logger.exception("Kaggle worker job failed: %s", job_id)
        outcome, _ = handle_attempt_failure(db, job_id, claimed_at, str(exc))
        return outcome
    finally:
        db.close()

if __name__ == "__main__":
    result = run_one_job()
    raise SystemExit(0 if result in {"empty", "completed", "scheduled", "exhausted"} else 1)