from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import update
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode, FailedJob, ProcessingJob
from ...services.processing import run_mock_job
from ..dependencies import get_current_user, require_roles

router = APIRouter(prefix="/jobs", tags=["jobs"])


class MockJobCreate(BaseModel):
    episode_id: str
    job_type: str = Field(default="mock_processing", max_length=40)


class RealJobCreate(BaseModel):
    episode_id: str
    job_type: str = Field(default="real_processing", max_length=40)


def _create_job(episode: Episode, job_type: str, db: Session) -> ProcessingJob:
    job = ProcessingJob(episode_id=episode.id, job_type=job_type, status="queued", progress=0)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.post("/mock", status_code=201)
def create_mock_job(payload: MockJobCreate, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    episode = db.get(Episode, payload.episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return run_mock_job(_create_job(episode, payload.job_type, db).id, db)


@router.post("/real", status_code=201)
def create_real_job(payload: RealJobCreate, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    episode = db.get(Episode, payload.episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return _create_job(episode, payload.job_type, db)


@router.get("")
def list_jobs(_: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(ProcessingJob).order_by(ProcessingJob.created_at.desc()).all()


@router.get("/{job_id}")
def get_job(job_id: str, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/retry")
def retry_job(job_id: str, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "failed":
        raise HTTPException(status_code=409, detail="Only failed jobs can be retried")

    exhausted = job.job_type == "real_processing" and job.retry_count >= job.max_retries
    current_retry_count = job.retry_count
    retry_count = 0 if exhausted else (
        current_retry_count + 1 if job.job_type != "real_processing" else current_retry_count
    )
    result = db.execute(
        update(ProcessingJob)
        .where(
            ProcessingJob.id == job_id,
            ProcessingJob.status == "failed",
            ProcessingJob.retry_count == current_retry_count,
            ProcessingJob.max_retries == job.max_retries,
        )
        .values(
            retry_count=retry_count,
            status="queued",
            progress=0,
            next_run_at=None,
            last_error=None,
            error_code=None,
            error_message=None,
            started_at=None,
            completed_at=None,
        )
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=409, detail="Job state changed; refresh and retry")
    if exhausted:
        db.execute(
            update(FailedJob)
            .where(
                FailedJob.processing_job_id == job_id,
                FailedJob.resolved_at.is_(None),
            )
            .values(resolved_at=datetime.now(timezone.utc))
        )
    db.commit()
    db.refresh(job)
    if job.job_type == "real_processing":
        return job
    return run_mock_job(job.id, db)
