from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode, ProcessingJob
from ...services.processing import run_mock_job
from ...services.real_processing import run_real_job
from ..dependencies import get_current_user

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
def create_mock_job(payload: MockJobCreate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    episode = db.get(Episode, payload.episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return run_mock_job(_create_job(episode, payload.job_type, db).id, db)


@router.post("/real", status_code=201)
def create_real_job(payload: RealJobCreate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    episode = db.get(Episode, payload.episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return run_real_job(_create_job(episode, payload.job_type, db).id, db)


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
def retry_job(job_id: str, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.get(ProcessingJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "failed":
        raise HTTPException(status_code=409, detail="Only failed jobs can be retried")
    job.retry_count += 1
    job.status = "queued"
    job.progress = 0
    job.error_code = None
    job.error_message = None
    job.completed_at = None
    db.commit()
    return run_real_job(job.id, db) if job.job_type == "real_processing" else run_mock_job(job.id, db)
