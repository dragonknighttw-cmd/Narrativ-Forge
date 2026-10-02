from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode, Script
from ..dependencies import get_current_user

router = APIRouter(prefix="/episodes", tags=["scripts"])
script_router = APIRouter(prefix="/scripts", tags=["scripts"])


class ScriptCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    content: str = Field(default="")


class ScriptUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    content: str | None = None
    status: str | None = Field(default=None, max_length=40)


class ScriptVersionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    content: str = Field(default="")


def _episode_or_404(db: Session, episode_id: str) -> Episode:
    item = db.get(Episode, episode_id)
    if not item:
        raise HTTPException(status_code=404, detail="Episode not found")
    return item


@router.get("/{episode_id}/scripts")
def list_scripts(episode_id: str, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id)
    return db.query(Script).filter(Script.episode_id == episode_id).order_by(Script.version.desc()).all()


@router.post("/{episode_id}/scripts", status_code=201)
def create_script(episode_id: str, payload: ScriptCreate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id)
    latest = db.query(func.max(Script.version)).filter(Script.episode_id == episode_id).scalar() or 0
    db.query(Script).filter(Script.episode_id == episode_id, Script.is_current.is_(True)).update({Script.is_current: False})
    item = Script(episode_id=episode_id, version=latest + 1, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@script_router.patch("/{script_id}")
def update_script(script_id: str, payload: ScriptUpdate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Script, script_id)
    if not item:
        raise HTTPException(status_code=404, detail="Script not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.post("/{episode_id}/scripts/versions", status_code=201)
def create_script_version(episode_id: str, payload: ScriptVersionCreate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id)
    latest = db.query(func.max(Script.version)).filter(Script.episode_id == episode_id).scalar() or 0
    db.query(Script).filter(Script.episode_id == episode_id, Script.is_current.is_(True)).update({Script.is_current: False})
    item = Script(episode_id=episode_id, version=latest + 1, title=payload.title, content=payload.content, status="draft", is_current=True)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
