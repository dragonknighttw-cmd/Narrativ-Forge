"""Local development worker for queued Narrativ Forge processing jobs.

Usage:
    python -m app.workers.mock_worker
"""

from app.core.config import settings
from app.db import SessionLocal, init_db
from app.models import ProcessingJob
from app.observability import configure_logging, initialize_sentry
from app.services.processing import run_mock_job


def main() -> None:
    configure_logging(settings.app_env)
    initialize_sentry(settings.sentry_dsn.get_secret_value(), settings.app_env)
    init_db()
    db = SessionLocal()
    try:
        jobs = (
            db.query(ProcessingJob)
            .filter(ProcessingJob.status == "queued")
            .order_by(ProcessingJob.created_at)
            .all()
        )
        for job in jobs:
            run_mock_job(job.id, db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
