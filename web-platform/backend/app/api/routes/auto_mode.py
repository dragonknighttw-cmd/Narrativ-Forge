from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode
from ...services.auto_mode import create_auto_plan
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
