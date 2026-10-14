import json
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Season, Series, SeriesBibleRecord
from ..dependencies import get_current_membership, get_current_user, require_roles

router = APIRouter(prefix="/series", tags=["series"])

class SeriesCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None

class SeriesUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: str | None = Field(default=None, max_length=40)

class SeasonCreate(BaseModel):
    season_number: int = Field(ge=1)
    title: str | None = Field(default=None, max_length=255)

class SeriesBibleCharacter(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=255)
    role: Literal["protagonist", "antagonist", "mentor", "sidekick"]
    tone: str = Field(default="", max_length=1000)
    catchphrase: str = Field(default="", max_length=1000)
    traits: str = Field(default="", max_length=2000)


class SeriesBibleUpdate(BaseModel):
    characters: list[SeriesBibleCharacter] = Field(default_factory=list, max_length=100)

@router.get("")
def list_series(membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    return db.query(Series).filter(Series.organization_id == membership.organization_id).order_by(Series.created_at.desc()).all()

@router.post("", status_code=201)
def create_series(payload: SeriesCreate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = Series(organization_id=membership.organization_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/{series_id}")
def get_series(series_id: str, membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    item = db.query(Series).filter(Series.id == series_id, Series.organization_id == membership.organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Series not found")
    return item

@router.patch("/{series_id}")
def update_series(series_id: str, payload: SeriesUpdate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.query(Series).filter(Series.id == series_id, Series.organization_id == membership.organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Series not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

@router.get("/{series_id}/bible")
def get_series_bible(series_id: str, membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.organization_id == membership.organization_id,
    ).first()
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    record = db.query(SeriesBibleRecord).filter(
        SeriesBibleRecord.series_id == series_id,
        SeriesBibleRecord.organization_id == membership.organization_id,
    ).first()
    return {
        "series_id": series_id,
        "characters": json.loads(record.characters_json) if record else [],
    }


@router.put("/{series_id}/bible")
def update_series_bible(
    series_id: str,
    payload: SeriesBibleUpdate,
    membership=Depends(get_current_membership),
    _: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    series = db.query(Series).filter(
        Series.id == series_id,
        Series.organization_id == membership.organization_id,
    ).first()
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    record = db.query(SeriesBibleRecord).filter(
        SeriesBibleRecord.series_id == series_id,
        SeriesBibleRecord.organization_id == membership.organization_id,
    ).first()
    if record is None:
        record = SeriesBibleRecord(
            organization_id=membership.organization_id,
            series_id=series_id,
        )
        db.add(record)
    record.characters_json = json.dumps(
        [character.model_dump() for character in payload.characters],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    db.commit()
    db.refresh(record)
    return {
        "series_id": series_id,
        "characters": json.loads(record.characters_json),
        "updated_at": record.updated_at.isoformat() if record.updated_at else None,
    }


@router.get("/{series_id}/seasons")
def list_seasons(series_id: str, membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    if not db.query(Series).filter(Series.id == series_id, Series.organization_id == membership.organization_id).first():
        raise HTTPException(status_code=404, detail="Series not found")
    return db.query(Season).filter(Season.series_id == series_id).order_by(Season.season_number.asc()).all()

@router.post("/{series_id}/seasons", status_code=201)
def create_season(series_id: str, payload: SeasonCreate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    if not db.query(Series).filter(Series.id == series_id, Series.organization_id == membership.organization_id).first():
        raise HTTPException(status_code=404, detail="Series not found")
    existing = db.query(Season).filter(Season.series_id == series_id, Season.season_number == payload.season_number).first()
    if existing:
        raise HTTPException(status_code=409, detail="Season number already exists in this series")
    item = Season(series_id=series_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
