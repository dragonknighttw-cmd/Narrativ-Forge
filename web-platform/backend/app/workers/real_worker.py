from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import ProcessingJob
from ..services.real_processing import run_real_job


def run_once(db: Session) -> int:
    jobs = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.job_type == "real_processing", ProcessingJob.status == "queued")
        .order_by(ProcessingJob.created_at.asc())
        .limit(5)
        .all()
    )
    for job in jobs:
        run_real_job(job.id, db)
    return len(jobs)


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print(f"processed_jobs={run_once(db)}")
    finally:
        db.close()
