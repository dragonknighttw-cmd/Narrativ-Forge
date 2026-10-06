from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Asset, Episode, ProcessingJob
from ...services.auto_mode import create_auto_plan
from ...services.selective_regeneration import regenerate_scene
from ..dependencies import require_roles

router = APIRouter(prefix="/auto", tags=["auto-mode"])


class AutoPlanRequest(BaseModel):
    idea: str = Field(min_length=1, max_length=10000)
    category: str | None = Field(default=None, max_length=100)


@router.post("/episodes/{episode_id}/plan")
def auto_plan(episode_id: str, payload: AutoPlanRequest, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    episode = db.get(Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    script, scenes = create_auto_plan(db, episode, payload.idea, payload.category)
    return {
        "episode_id": episode.id,
        "script": {
            "id": script.id,
            "version": script.version,
            "status": script.status,
            "content": script.content,
        },
        "scenes": [
            {
                "id": scene.id,
                "scene_number": scene.scene_number,
                "purpose": scene.purpose,
                "description": scene.description,
                "dialogue": scene.dialogue,
                "duration_seconds": scene.duration_seconds,
            }
            for scene in scenes
        ],
        "next_step": episode.current_step,
        "requires_human_review": True,
    }


@router.post("/episodes/{episode_id}/run")
def run_auto_mode(episode_id: str, payload: AutoPlanRequest, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    episode = db.get(Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    active = db.query(ProcessingJob).filter(
        ProcessingJob.episode_id == episode_id,
        ProcessingJob.status.in_(["queued", "running"]),
    ).first()
    if active:
        raise HTTPException(status_code=409, detail="Episode already has an active processing job")
    source = db.query(Asset).filter(
        Asset.episode_id == episode_id,
        Asset.asset_type == "video",
        Asset.status == "uploaded",
    ).order_by(Asset.version.desc()).first()
    if not source:
        raise HTTPException(status_code=409, detail="Upload a source video before starting Auto Mode")
    script, scenes = create_auto_plan(db, episode, payload.idea, payload.category)
    job = ProcessingJob(
        episode_id=episode_id,
        job_type="real_processing",
        status="queued",
        progress=0,
        input_asset_id=source.id,
    )
    db.add(job)
    episode.current_step = "processing"
    episode.status = "in_production"
    db.commit()
    db.refresh(job)
    return {
        "episode_id": episode_id,
        "script_id": script.id,
        "scene_count": len(scenes),
        "job_id": job.id,
        "status": job.status,
        "next_steps": ["processing", "subtitle", "review"],
        "requires_human_review": True,
    }


class SceneRegenerationRequest(BaseModel):
    instruction: str = Field(min_length=1, max_length=2000)


@router.post("/episodes/{episode_id}/scenes/{scene_number}/regenerate")
def regenerate_episode_scene(
    episode_id: str,
    scene_number: int,
    payload: SceneRegenerationRequest,
    _: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    episode = db.get(Episode, episode_id)
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    try:
        script, scenes = regenerate_scene(db, episode, scene_number, payload.instruction)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "episode_id": episode.id,
        "script_id": script.id,
        "version": script.version,
        "scene_number": scene_number,
        "scenes": [
            {
                "id": scene.id,
                "scene_number": scene.scene_number,
                "purpose": scene.purpose,
                "description": scene.description,
                "dialogue": scene.dialogue,
                "duration_seconds": scene.duration_seconds,
            }
            for scene in scenes
        ],
        "requires_human_review": True,
    }
