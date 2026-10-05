import logging
import time
from datetime import datetime, timezone

from sqlalchemy import or_, update
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db import SessionLocal
from ..models import FailedJob, ProcessingJob
from ..observability import configure_logging, initialize_sentry
from .celery_app import get_celery
from .tasks import enqueue_real_job, publish_dead_letter

logger = logging.getLogger(__name__)
POLL_INTERVAL_SECONDS = 5
BATCH_SIZE = 5


def run_once(db: Session) -> int:
    celery = get_celery()
    now = datetime.now(timezone.utc)
    jobs = (
        db.query(ProcessingJob)
        .filter(
            ProcessingJob.job_type == "real_processing",
            ProcessingJob.status == "queued",
            or_(ProcessingJob.next_run_at.is_(None), ProcessingJob.next_run_at <= now),
        )
        .order_by(ProcessingJob.created_at.asc())
        .limit(BATCH_SIZE)
        .all()
    )
    dispatched = 0
    for job in jobs:
        if enqueue_real_job(job.id):
            dispatched += 1
    pending_failed_jobs = (
        db.query(FailedJob)
        .filter(FailedJob.resolved_at.is_(None), FailedJob.dlq_published_at.is_(None))
        .order_by(FailedJob.created_at.asc())
        .limit(BATCH_SIZE)
        .all()
    )
    for failed_job in pending_failed_jobs:
        if publish_dead_letter(celery, db, failed_job.id):
            dispatched += 1
    return dispatched


def run_forever(poll_interval: int = POLL_INTERVAL_SECONDS, sleep_fn=None) -> None:
    if sleep_fn is None:
        sleep_fn = time.sleep

    while True:
        db = SessionLocal()
        try:
            try:
                run_once(db)
            except Exception:
                logger.exception("Dispatcher cycle failed; queued jobs remain eligible for dispatch")
        finally:
            db.close()
        sleep_fn(poll_interval)


if __name__ == "__main__":
    configure_logging(settings.app_env)
    initialize_sentry(settings.sentry_dsn.get_secret_value(), settings.app_env)
    get_celery()
    run_forever()
