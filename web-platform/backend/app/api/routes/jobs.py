from datetime import datetime, timezone
import json
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from sqlalchemy import update
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode, FailedJob, ProcessingJob, UsageEvent
from ...middleware.idempotency import (
    IdempotencyClaim,
    StoredResponse,
    begin_idempotency,
    complete_idempotency,
    request_fingerprint,
    validate_idempotency_key,
)
from ...services.processing import run_mock_job
from ...workers.tasks import enqueue_real_job
from ..dependencies import get_current_membership, get_current_user, require_roles

router = APIRouter(prefix="/jobs", tags=["jobs"])


class MockJobCreate(BaseModel):
    episode_id: str
    job_type: str = Field(default="mock_processing", max_length=40)


class RealJobCreate(BaseModel):
    episode_id: str
    job_type: str = Field(default="real_processing", max_length=40)



def _meter_processing_job(db: Session, organization_id: str, job: ProcessingJob) -> None:
    period_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if db.query(UsageEvent).filter(UsageEvent.idempotency_key == f"job:{job.id}").first():
        return
    db.add(UsageEvent(organization_id=organization_id, metric="processing_jobs", quantity=1, unit="job", idempotency_key=f"job:{job.id}", period_start=period_start, metadata_json=json.dumps({"job_id": job.id, "job_type": job.job_type}, separators=(",", ":"))))

def _create_job(
    episode: Episode,
    job_type: str,
    db: Session,
    *,
    job_id: str | None = None,
    commit: bool = True,
) -> ProcessingJob:
    job = ProcessingJob(
        id=job_id or str(uuid4()),
        episode_id=episode.id,
        job_type=job_type,
        status="queued",
        progress=0,
    )
    db.add(job)
    db.flush()
    if commit:
        db.commit()
        db.refresh(job)
    return job


@router.post("/mock", status_code=201)
def create_mock_job(
    payload: MockJobCreate,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: dict = Depends(require_roles("owner", "editor")),
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    idempotency_key = validate_idempotency_key(idempotency_key)
    episode = db.query(Episode).filter(Episode.id == payload.episode_id, Episode.organization_id == membership.organization_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    claim_or_response = begin_idempotency(
        db,
        actor_id=user["id"],
        key=idempotency_key,
        method=request.method,
        target=request.url.path,
        fingerprint=request_fingerprint(request.method, request.url.path, payload.model_dump(mode="json")),
        resource_type="processing_job",
    )
    if isinstance(claim_or_response, StoredResponse):
        return claim_or_response.response()
    if isinstance(claim_or_response, IdempotencyClaim) and not claim_or_response.created:
        job = db.get(ProcessingJob, claim_or_response.record.resource_id)
        if not job:
            raise HTTPException(status_code=409, detail="Job request is still processing")
        stored_response = complete_idempotency(
            claim_or_response,
            jsonable_encoder(job),
            status_code=201,
        )
        db.commit()
        return stored_response.response()
    claim = claim_or_response if isinstance(claim_or_response, IdempotencyClaim) else None
    job = _create_job(
        episode,
        payload.job_type,
        db,
        job_id=claim.record.resource_id if claim else None,
        commit=claim is None,
    )
    _meter_processing_job(db, membership.organization_id, job)
    if not claim:
        return run_mock_job(job.id, db)

    db.commit()
    result = run_mock_job(job.id, db)
    stored_response = complete_idempotency(claim, jsonable_encoder(result), status_code=201)
    db.commit()
    return stored_response.response()


@router.post("/real", status_code=201)
def create_real_job(
    payload: RealJobCreate,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: dict = Depends(require_roles("owner", "editor")),
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    idempotency_key = validate_idempotency_key(idempotency_key)
    episode = db.query(Episode).filter(Episode.id == payload.episode_id, Episode.organization_id == membership.organization_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    claim_or_response = begin_idempotency(
        db,
        actor_id=user["id"],
        key=idempotency_key,
        method=request.method,
        target=request.url.path,
        fingerprint=request_fingerprint(request.method, request.url.path, payload.model_dump(mode="json")),
        resource_type="processing_job",
    )
    if isinstance(claim_or_response, StoredResponse):
        return claim_or_response.response()
    if isinstance(claim_or_response, IdempotencyClaim) and not claim_or_response.created:
        job = db.get(ProcessingJob, claim_or_response.record.resource_id)
        if not job:
            raise HTTPException(status_code=409, detail="Job request is still processing")
        stored_response = complete_idempotency(
            claim_or_response,
            jsonable_encoder(job),
            status_code=201,
        )
        db.commit()
        return stored_response.response()
    claim = claim_or_response if isinstance(claim_or_response, IdempotencyClaim) else None
    job = _create_job(
        episode,
        payload.job_type,
        db,
        job_id=claim.record.resource_id if claim else None,
        commit=claim is None,
    )
    _meter_processing_job(db, membership.organization_id, job)
    if not claim:
        db.commit()
        enqueue_real_job(job.id)
        return job
    stored_response = complete_idempotency(claim, jsonable_encoder(job), status_code=201)
    db.commit()
    enqueue_real_job(job.id)
    return stored_response.response()


@router.get("")
def list_jobs(membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    return db.query(ProcessingJob).join(Episode, ProcessingJob.episode_id == Episode.id).filter(Episode.organization_id == membership.organization_id).order_by(ProcessingJob.created_at.desc()).all()


@router.get("/{job_id}")
def get_job(job_id: str, membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).join(Episode, ProcessingJob.episode_id == Episode.id).filter(ProcessingJob.id == job_id, Episode.organization_id == membership.organization_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/retry")
def retry_job(job_id: str, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).join(Episode, ProcessingJob.episode_id == Episode.id).filter(ProcessingJob.id == job_id, Episode.organization_id == membership.organization_id).first()
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
