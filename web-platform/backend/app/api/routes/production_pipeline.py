from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode
from ...services.hook_engineering import generate_hook_candidates
from ...services.production_pipeline import (
    build_ab_variants,
    build_cross_platform_export_plan,
    build_production_metadata,
    plan_batch,
)
from ..dependencies import get_current_membership, require_roles


router = APIRouter(prefix="/production", tags=["production-pipeline"])


class MetadataRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    topic: str = Field(min_length=1, max_length=300)
    hook: str = Field(min_length=1, max_length=300)
    keywords: list[str] = Field(default_factory=list, max_length=12)
    category: str | None = Field(default=None, max_length=100)


class BatchRequest(BaseModel):
    episode_ids: list[str] = Field(min_length=1, max_length=100)
    platform: str = Field(default="youtube_shorts", max_length=40)
    start_at: datetime | None = None
    interval_minutes: int = Field(default=60, ge=1, le=10080)


class ABRequest(BaseModel):
    hooks: list[str] = Field(min_length=1, max_length=10)
    thumbnail_texts: list[str] = Field(min_length=1, max_length=10)


@router.get("/episodes/{episode_id}/hooks")
def episode_hooks(
    episode_id: str,
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    episode = db.query(Episode).filter(
        Episode.id == episode_id,
        Episode.organization_id == membership.organization_id,
    ).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return generate_hook_candidates(episode.title, category=episode.category)


@router.post("/metadata")
def production_metadata(
    payload: MetadataRequest,
    membership=Depends(get_current_membership),
    _: dict = Depends(require_roles("owner", "editor")),
):
    metadata = build_production_metadata(
        payload.title,
        payload.topic,
        payload.hook,
        payload.keywords,
        payload.category,
    )
    return {
        "title": metadata.title,
        "description": metadata.description,
        "hashtags": metadata.hashtags,
        "thumbnail_text": metadata.thumbnail_text,
        "thumbnail_prompt": metadata.thumbnail_prompt,
        "sound_plan": metadata.sound_plan,
        "platform_exports": metadata.platform_exports,
    }


@router.post("/batch/plan")
def production_batch_plan(
    payload: BatchRequest,
    membership=Depends(get_current_membership),
    _: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    found = db.query(Episode).filter(
        Episode.id.in_(payload.episode_ids),
        Episode.organization_id == membership.organization_id,
    ).all()
    found_ids = {item.id for item in found}
    missing = [item for item in payload.episode_ids if item not in found_ids]
    if missing:
        raise HTTPException(status_code=404, detail={"message": "Some episodes were not found", "episode_ids": missing})
    rows = plan_batch(
        [{"key": item} for item in payload.episode_ids],
        platform=payload.platform,
        start_at=payload.start_at,
        interval_minutes=payload.interval_minutes,
    )
    return [row.__dict__ for row in rows]


@router.post("/ab/variants")
def ab_variants(
    payload: ABRequest,
    membership=Depends(get_current_membership),
    _: dict = Depends(require_roles("owner", "editor")),
):
    return [item.__dict__ for item in build_ab_variants(payload.hooks, payload.thumbnail_texts)]


@router.get("/episodes/{episode_id}/exports")
def episode_export_plan(
    episode_id: str,
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    episode = db.query(Episode).filter(
        Episode.id == episode_id,
        Episode.organization_id == membership.organization_id,
    ).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return build_cross_platform_export_plan(episode.target_duration_seconds)
