from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode, Scene, Script
from ...services.hook_engineering import generate_hook_candidates
from ...services.series_continuity import build_series_bible, check_continuity
from ...services.production_pipeline import (
    build_ab_variants,
    build_cross_platform_export_plan,
    build_production_metadata,
    plan_batch,
    assess_production_readiness,
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


@router.get("/episodes/{episode_id}/readiness")
def episode_readiness(
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

    script = db.query(Script).filter(
        Script.episode_id == episode.id,
        Script.is_current.is_(True),
    ).first()
    if not script:
        return {
            "episode_id": episode.id,
            "ready_for_review": False,
            "quality_score": 0,
            "quality_issues": ["current_script_missing"],
            "continuity_issues": [],
        }

    scenes = db.query(Scene).filter(
        Scene.script_id == script.id,
    ).order_by(Scene.scene_number.asc()).all()
    bible = build_series_bible(
        episode.series.title if episode.series else "",
        episode.series.description if episode.series else "",
    )
    continuity = check_continuity(
        bible,
        title=episode.title,
        synopsis=episode.synopsis or script.content,
    )
    readiness = assess_production_readiness(
        script=script.content,
        scene_durations=[scene.duration_seconds for scene in scenes],
        target_seconds=episode.target_duration_seconds,
        continuity_issues=[issue.message for issue in continuity],
    )
    return {
        "episode_id": episode.id,
        "script_id": script.id,
        "quality_score": readiness.quality_score,
        "quality_issues": readiness.quality_issues,
        "continuity_issues": readiness.continuity_issues,
        "ready_for_review": readiness.ready_for_review,
    }


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
