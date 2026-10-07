from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from sqlalchemy import func, update
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode, Script
from ..dependencies import get_current_membership, get_current_user, require_roles

router = APIRouter(prefix="/episodes", tags=["scripts"])
script_router = APIRouter(prefix="/scripts", tags=["scripts"])


class ScriptCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    content: str = Field(default="")


class ScriptUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    content: str | None = None
    status: str | None = Field(default=None, max_length=40)
    expected_row_version: int = Field(ge=1)


class ScriptVersionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    content: str = Field(default="")


def _episode_or_404(db: Session, episode_id: str, organization_id: str | None = None) -> Episode:
    item = db.query(Episode).filter(Episode.id == episode_id, *( [Episode.organization_id == organization_id] if organization_id else [] )).first()
    if not item:
        raise HTTPException(status_code=404, detail="Episode not found")
    return item


@router.get("/{episode_id}/scripts")
def list_scripts(episode_id: str, limit: int = Query(default=50, ge=1, le=100), offset: int = Query(default=0, ge=0), membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id, membership.organization_id)
    return db.query(Script).filter(Script.episode_id == episode_id).order_by(Script.version.desc()).offset(offset).limit(limit).all()


@router.post("/{episode_id}/scripts", status_code=201)
def create_script(episode_id: str, payload: ScriptCreate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id, membership.organization_id)
    latest = db.query(func.max(Script.version)).filter(Script.episode_id == episode_id).scalar() or 0
    db.query(Script).filter(Script.episode_id == episode_id, Script.is_current.is_(True)).update({Script.is_current: False})
    item = Script(episode_id=episode_id, version=latest + 1, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@script_router.patch("/{script_id}")
def update_script(script_id: str, payload: ScriptUpdate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.query(Script).join(Episode, Script.episode_id == Episode.id).filter(Script.id == script_id, Episode.organization_id == membership.organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Script not found")

    if not item.is_current:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "HISTORICAL_SCRIPT_IMMUTABLE",
                "message": "Historical script versions are immutable; create a new version instead",
            },
        )

    data = payload.model_dump(exclude={"expected_row_version"}, exclude_unset=True)
    data["row_version"] = Script.row_version + 1
    data["updated_at"] = datetime.now(timezone.utc)
    result = db.execute(
        update(Script)
        .where(Script.id == script_id, Script.row_version == payload.expected_row_version)
        .values(**data)
    )
    if result.rowcount != 1:
        db.rollback()
        current = db.get(Script, script_id)
        if not current:
            raise HTTPException(status_code=404, detail="Script not found")
        raise HTTPException(
            status_code=409,
            detail={
                "code": "STALE_ROW_VERSION",
                "message": "Script was modified by another request",
                "current": jsonable_encoder(current),
            },
        )

    db.commit()
    db.refresh(item)
    return item


@router.post("/{episode_id}/scripts/versions", status_code=201)
def create_script_version(episode_id: str, payload: ScriptVersionCreate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id, membership.organization_id)
    latest = db.query(func.max(Script.version)).filter(Script.episode_id == episode_id).scalar() or 0
    db.query(Script).filter(Script.episode_id == episode_id, Script.is_current.is_(True)).update({Script.is_current: False})
    item = Script(episode_id=episode_id, version=latest + 1, title=payload.title, content=payload.content, status="draft", is_current=True)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
