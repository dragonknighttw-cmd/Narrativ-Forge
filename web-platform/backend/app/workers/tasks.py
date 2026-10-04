from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from .celery_app import get_celery
from .. import db as app_db
from ..models import ProcessingJob
from ..services.real_processing import run_real_job


def _now() -> datetime:
    return datetime.now(timezone.utc)


def register_tasks(celery_app):
    """Register tasks on the provided Celery app instance.

    This approach avoids requiring a broker at import time. Tests can create a
    Celery instance (for example with an in-memory broker) and call
    `register_tasks(celery)` to bind the tasks for test execution.
    """

    @celery_app.task(name="narrativ.process_real_job")
    def process_real_job_task(job_id: str) -> str:
        """Celery task wrapper that runs the existing real processing logic.

        The task creates and closes its own DB session. It loads the
        ProcessingJob by ID and only processes queued jobs. On errors the
        job row is updated with failure data to preserve the existing
        domain error model.
        """

        db: Optional[Session] = None
        try:
            db = app_db.SessionLocal()
            job = db.get(ProcessingJob, job_id)
            if not job:
                raise RuntimeError("Processing job not found")
            # Do not re-run completed jobs
            if job.status == "completed":
                return job.id

            # Mark running and commit small transaction before heavy work
            job.status = "running"
            job.progress = 0
            job.started_at = _now()
            job.error_code = None
            job.error_message = None
            db.commit()

            # Run the existing real-processing function with a fresh session
            # The implementation of run_real_job is responsible for updating
            # job.status to completed/failed as appropriate; if it raises,
            # fall through to the exception handler below and mark job failed.
            run_real_job(job.id, db)

            return job.id
        except Exception as exc:  # pylint: disable=broad-except
            # Try to mark the job as failed using the DB connection; be robust
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
                # If updating the job row fails, logging/monitoring should
                # catch this in real deployments. Here, just re-raise.
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
