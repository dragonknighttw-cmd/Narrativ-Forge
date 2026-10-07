from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode, Scene, Script
from ..dependencies import get_current_membership, get_current_user, require_roles

router = APIRouter(prefix="/episodes", tags=["scenes"])
scene_router = APIRouter(prefix="/scenes", tags=["scenes"])


class SceneCreate(BaseModel):
    scene_number: int = Field(ge=1)
    script_id: str | None = None
    purpose: str = Field(min_length=1, max_length=255)
    description: str | None = None
    dialogue: str | None = None
    duration_seconds: int | None = Field(default=None, ge=1)


class SceneUpdate(BaseModel):
    scene_number: int | None = Field(default=None, ge=1)
    script_id: str | None = None
    purpose: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    dialogue: str | None = None
    duration_seconds: int | None = Field(default=None, ge=1)


def _episode_or_404(db: Session, episode_id: str, organization_id: str | None = None) -> Episode:
    item = db.query(Episode).filter(Episode.id == episode_id, *( [Episode.organization_id == organization_id] if organization_id else [] )).first()
    if not item:
        raise HTTPException(status_code=404, detail="Episode not found")
    return item


def _validate_script(db: Session, episode_id: str, script_id: str | None) -> None:
    if script_id:
        script = db.get(Script, script_id)
        if not script or script.episode_id != episode_id:
            raise HTTPException(status_code=422, detail="Script does not belong to this episode")


@router.get("/{episode_id}/scenes")
def list_scenes(episode_id: str, membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id, membership.organization_id)
    return db.query(Scene).filter(Scene.episode_id == episode_id).order_by(Scene.scene_number).all()


@router.post("/{episode_id}/scenes", status_code=201)
def create_scene(episode_id: str, payload: SceneCreate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id, membership.organization_id)
    _validate_script(db, episode_id, payload.script_id)
    if db.query(Scene).filter(Scene.episode_id == episode_id, Scene.scene_number == payload.scene_number).first():
        raise HTTPException(status_code=409, detail="Scene number already exists")
    item = Scene(episode_id=episode_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@scene_router.patch("/{scene_id}")
def update_scene(scene_id: str, payload: SceneUpdate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.query(Scene).join(Episode, Scene.episode_id == Episode.id).filter(Scene.id == scene_id, Episode.organization_id == membership.organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Scene not found")
    episode_id = item.episode_id
    values = payload.model_dump(exclude_unset=True)
    _validate_script(db, episode_id, values.get("script_id"))
    if "scene_number" in values and values["scene_number"] != item.scene_number:
        if db.query(Scene).filter(Scene.episode_id == episode_id, Scene.scene_number == values["scene_number"]).first():
            raise HTTPException(status_code=409, detail="Scene number already exists")
    for key, value in values.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.post("/{episode_id}/scenes/reorder")
def reorder_scenes(episode_id: str, scene_ids: list[str], membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id, membership.organization_id)
    scenes = db.query(Scene).filter(Scene.episode_id == episode_id).all()
    by_id = {scene.id: scene for scene in scenes}
    if len(scene_ids) != len(scenes) or set(scene_ids) != set(by_id):
        raise HTTPException(status_code=422, detail="scene_ids must contain every scene exactly once")
    for index, scene_id in enumerate(scene_ids, start=1):
        by_id[scene_id].scene_number = index
    db.commit()
    return db.query(Scene).filter(Scene.episode_id == episode_id).order_by(Scene.scene_number).all()
