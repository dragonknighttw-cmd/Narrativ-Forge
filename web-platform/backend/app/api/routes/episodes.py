from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode, Season, Series
from ..dependencies import get_current_user

router = APIRouter(prefix="/episodes", tags=["episodes"])

VALID_STATUSES = {
    "idea","planned","script_draft","script_review","assets_needed","in_production",
    "processing","subtitle_review","needs_approval","approved","exporting","exported",
    "archived","rejected","failed"
}
STEP_BY_STATUS = {\n    "idea": "idea", "planned": "structure", "script_draft": "script", "script_review": "script",\n    "assets_needed": "assets", "in_production": "production", "processing": "processing",\n    "subtitle_review": "subtitle", "needs_approval": "review", "approved": "review",\n    "exporting": "output", "exported": "output", "archived": "output", "rejected": "review", "failed": "processing",\n}\n\nSTATUS_TRANSITIONS = {
    "idea": {"planned"},
    "planned": {"script_draft"},
    "script_draft": {"script_review"},
    "script_review": {"assets_needed", "script_draft"},
    "assets_needed": {"in_production"},
    "in_production": {"processing"},
    "processing": {"subtitle_review"},
    "subtitle_review": {"needs_approval", "in_production"},
    "needs_approval": {"approved", "in_production"},
    "approved": {"exporting"},
    "exporting": {"exported", "failed"},
    "exported": {"archived"},
    "archived": set(),
    "rejected": set(),
    "failed": {"processing"},
}

class EpisodeCreate(BaseModel):
    public_id: str | None = Field(default=None, max_length=40)
    series_id: str
    season_id: str | None = None
    episode_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    synopsis: str | None = None
    target_duration_seconds: int = Field(default=180, ge=1)

class EpisodeUpdate(BaseModel):
    season_id: str | None = None
    episode_number: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    synopsis: str | None = None
    target_duration_seconds: int | None = Field(default=None, ge=1)
    actual_duration_seconds: int | None = Field(default=None, ge=0)
    status: str | None = None
    current_step: str | None = Field(default=None, max_length=40)

def generated_public_id(db: Session) -> str:
    prefix = date.today().strftime("nar_%Y%m%d_")
    count = db.query(Episode).filter(Episode.public_id.like(prefix + "%")).count()
    return f"{prefix}{count + 1:04d}"

def validate_structure(db: Session, series_id: str, season_id: str | None):
    series = db.get(Series, series_id)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    if season_id:
        season = db.get(Season, season_id)
        if not season or season.series_id != series_id:
            raise HTTPException(status_code=400, detail="Season does not belong to this series")

@router.get("")
def list_episodes(_: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Episode).order_by(Episode.created_at.desc()).all()

@router.post("", status_code=201)
def create_episode(payload: EpisodeCreate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    validate_structure(db, payload.series_id, payload.season_id)
    if payload.season_id and db.query(Episode).filter(Episode.season_id == payload.season_id, Episode.episode_number == payload.episode_number).first():
        raise HTTPException(status_code=409, detail="Episode number already exists in this season")
    public_id = payload.public_id or generated_public_id(db)
    if db.query(Episode).filter(Episode.public_id == public_id).first():
        raise HTTPException(status_code=409, detail="Public ID already exists")
    item = Episode(public_id=public_id, **payload.model_dump(exclude={"public_id"}))
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/{episode_id}")
def get_episode(episode_id: str, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Episode, episode_id)
    if not item:
        raise HTTPException(status_code=404, detail="Episode not found")
    return item

@router.patch("/{episode_id}")
def update_episode(episode_id: str, payload: EpisodeUpdate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Episode, episode_id)
    if not item:
        raise HTTPException(status_code=404, detail="Episode not found")
    data = payload.model_dump(exclude_unset=True)
    if "status" in data:
        status = data["status"]
        if status not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail="Invalid episode status")
        if status != item.status and status not in STATUS_TRANSITIONS.get(item.status, set()):
            raise HTTPException(status_code=409, detail=f"Invalid status transition: {item.status} -> {status}")
    season_id = data.get("season_id", item.season_id)
    validate_structure(db, item.series_id, season_id)
    number = data.get("episode_number", item.episode_number)
    if season_id and db.query(Episode).filter(Episode.id != item.id, Episode.season_id == season_id, Episode.episode_number == number).first():
        raise HTTPException(status_code=409, detail="Episode number already exists in this season")
    for key, value in data.items():
        setattr(item, key, value)
    if "status" in data:
        item.current_step = STEP_BY_STATUS[data["status"]]
    db.commit()
    db.refresh(item)
    return item
