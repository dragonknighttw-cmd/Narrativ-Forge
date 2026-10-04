import logging
import time

from sqlalchemy.orm import Session

from ..core.config import settings
from ..db import SessionLocal
from ..models import ProcessingJob
from ..observability import configure_logging, initialize_sentry
from .celery_app import get_celery

logger = logging.getLogger(__name__)
POLL_INTERVAL_SECONDS = 5
BATCH_SIZE = 5


def run_once(db: Session) -> int:
    celery = get_celery()
    jobs = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.job_type == "real_processing", ProcessingJob.status == "queued")
        .order_by(ProcessingJob.created_at.asc())
        .limit(BATCH_SIZE)
        .all()
    )
    for job in jobs:
        celery.send_task("narrativ.process_real_job", args=[job.id])
    return len(jobs)


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
