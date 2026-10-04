from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from .celery_app import get_celery
from .. import db as app_db
from ..models import ProcessingJob
from ..services.real_processing import run_real_job


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _claim_job(db: Session, job_id: str) -> bool:
    """Atomically claim a queued job before expensive processing begins."""
    result = db.execute(
        update(ProcessingJob)
        .where(ProcessingJob.id == job_id, ProcessingJob.status == "queued")
        .values(
            status="running",
            progress=0,
            started_at=_now(),
            error_code=None,
            error_message=None,
            completed_at=None,
        )
    )
    db.commit()
    return result.rowcount > 0


def register_tasks(celery_app):
    """Register tasks on the provided Celery app instance.

    This approach avoids requiring a broker at import time. Tests can create a
    Celery instance (for example with an in-memory broker) and call
    `register_tasks(celery)` to bind the tasks for test execution.
    """

    @celery_app.task(name="narrativ.process_real_job")
    def process_real_job_task(job_id: str) -> str:
        """Celery task wrapper that runs the existing real processing logic.

        The task creates and closes its own DB session. It atomically claims the
        job before invoking the existing processing engine. On errors the job row
        is updated with failure data to preserve the existing domain error model.
        """

        db: Optional[Session] = None
        try:
            db = app_db.SessionLocal()
            job = db.get(ProcessingJob, job_id)
            if not job:
                raise RuntimeError("Processing job not found")
            if job.status in {"completed", "running"}:
                return job.id

            claimed = _claim_job(db, job_id)
            if not claimed:
                job = db.get(ProcessingJob, job_id)
                if job is None:
                    raise RuntimeError("Processing job not found")
                if job.status in {"completed", "running"}:
                    return job.id
                return job.id

            run_real_job(job_id, db)
            return job_id
        except Exception as exc:  # pylint: disable=broad-except
            try:
                if db is None:
                    db = app_db.SessionLocal()
                job = db.get(ProcessingJob, job_id)
                if job:
                    job.status = "failed"
                    job.error_message = str(exc)
                    job.completed_at = _now()
                    db.commit()
            except Exception:
                pass
            raise
        finally:
            if db is not None:
                try:
                    db.close()
                except Exception:
                    pass

    return process_real_job_task


# Optional convenience: if a Celery app exists in the environment, register
# tasks automatically. Tests should call register_tasks explicitly with a
# test Celery instance to avoid depending on a live broker.
_env_celery = get_celery(allow_missing=True)
if _env_celery is not None:
    register_tasks(_env_celery)
