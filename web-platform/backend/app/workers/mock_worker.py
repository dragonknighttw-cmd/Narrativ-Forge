"""Local development worker for queued Narrativ Forge processing jobs.

Usage:
    python -m app.workers.mock_worker
"""

from app.db import SessionLocal, init_db
from app.models import ProcessingJob
from app.services.processing import run_mock_job


def main() -> None:
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
