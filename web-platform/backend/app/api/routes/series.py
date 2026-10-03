from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, selectinload

from ...db import get_db
from ...models import Season, Series
from ..dependencies import get_current_user, require_roles

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

@router.get("")
def list_series(_: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Series).options(selectinload(Series.seasons)).order_by(Series.created_at.desc()).all()

@router.post("", status_code=201)
def create_series(payload: SeriesCreate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = Series(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/{series_id}")
def get_series(series_id: str, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Series, series_id)
    if not item:
        raise HTTPException(status_code=404, detail="Series not found")
    return item

@router.patch("/{series_id}")
def update_series(series_id: str, payload: SeriesUpdate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Series, series_id)
    if not item:
        raise HTTPException(status_code=404, detail="Series not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

@router.get("/{series_id}/seasons")
def list_seasons(series_id: str, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.get(Series, series_id):
        raise HTTPException(status_code=404, detail="Series not found")
    return db.query(Season).filter(Season.series_id == series_id).order_by(Season.season_number.asc()).all()

@router.post("/{series_id}/seasons", status_code=201)
def create_season(series_id: str, payload: SeasonCreate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not db.get(Series, series_id):
        raise HTTPException(status_code=404, detail="Series not found")
    existing = db.query(Season).filter(Season.series_id == series_id, Season.season_number == payload.season_number).first()
    if existing:
        raise HTTPException(status_code=409, detail="Season number already exists in this series")
    item = Season(series_id=series_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
