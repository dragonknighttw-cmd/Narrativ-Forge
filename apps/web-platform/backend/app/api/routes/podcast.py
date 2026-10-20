from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.podcast_engine import generate_burmese_duo_podcast, PODCAST_TEMPLATES

router = APIRouter(prefix="/podcast", tags=["podcast"])

class GeneratePodcastRequest(BaseModel):
    topic: str
    synopsis: str
    template_key: Optional[str] = "cinema_deep_dive"

@router.get("/templates")
async def get_podcast_templates():
    return {
        "status": "success",
        "templates": [
            {"key": k, "title": v["title"], "bgm": v["bgm_preset"]}
            for k, v in PODCAST_TEMPLATES.items()
        ]
    }

@router.post("/generate-duo")
async def generate_duo_episode(req: GeneratePodcastRequest):
    result = generate_burmese_duo_podcast(
        topic=req.topic,
        synopsis=req.synopsis,
        template_key=req.template_key or "cinema_deep_dive"
    )
    return result
