from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...db import get_db
from ...models import Episode
from ..dependencies import get_current_user

router = APIRouter(prefix="/episodes", tags=["episodes"])

VALID_STATUSES = {
    "idea","planned","script_draft","script_review","assets_needed","in_production",
    "processing","subtitle_review","needs_approval","approved","exporting","exported",
    "archived","rejected","failed"
}

class EpisodeCreate(BaseModel):
    public_id: str
    series_id: str
    season_id: str | None = None
    episode_number: int
    title: str
    category: str | None = None
    synopsis: str | None = None
    target_duration_seconds: int = 180

@router.get("")
def list_episodes(_: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Episode).order_by(Episode.created_at.desc()).all()

@router.post("")
def create_episode(payload: EpisodeCreate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = Episode(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
