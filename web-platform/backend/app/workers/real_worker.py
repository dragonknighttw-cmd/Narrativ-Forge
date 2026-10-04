from sqlalchemy.orm import Session

from ..core.config import settings
from ..db import SessionLocal
from ..models import ProcessingJob
from ..observability import configure_logging, initialize_sentry
from .celery_app import get_celery


def run_once(db: Session) -> int:
    celery = get_celery()
    jobs = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.job_type == "real_processing", ProcessingJob.status == "queued")
        .order_by(ProcessingJob.created_at.asc())
        .limit(5)
        .all()
    )
    for job in jobs:
        celery.send_task("narrativ.process_real_job", args=[job.id])
    return len(jobs)


if __name__ == "__main__":
    configure_logging(settings.app_env)
    initialize_sentry(settings.sentry_dsn.get_secret_value(), settings.app_env)
    db = SessionLocal()
    try:
        print(f"dispatched_jobs={run_once(db)}")
    finally:
        db.close()
