from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...services.recap_engine import (
    RECAP_TEMPLATES,
    generate_burmese_recap_script,
    simulate_auto_video_edit,
)

logger = logging.getLogger("narrativ.api.recap")

router = APIRouter(prefix="/recap", tags=["Movie Recap & Auto Editing"])


class GenerateScriptRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, example="Parasite (2019)")
    synopsis: Optional[str] = Field(default="", max_length=5000, example="A poor family schemes to become employed by a wealthy family.")
    template_id: str = Field(default="thriller_suspense", example="thriller_suspense")
    duration_seconds: int = Field(default=90, ge=30, le=600, example=90)


class AutoEditRequest(BaseModel):
    recap_script: Dict[str, Any]
    aspect_ratio: str = Field(default="9:16", example="9:16")
    subtitle_style: str = Field(default="tiktok_yellow", example="tiktok_yellow")


@router.get("/templates")
async def get_recap_templates() -> Dict[str, Any]:
    """Retrieve pre-configured Burmese movie recap style templates."""
    return {"templates": RECAP_TEMPLATES}


@router.post("/generate-script")
async def api_generate_script(payload: GenerateScriptRequest) -> Dict[str, Any]:
    """
    Generate scene-by-scene Burmese movie recap narration script with timestamps.
    """
    try:
        result = generate_burmese_recap_script(
            title=payload.title,
            synopsis=payload.synopsis or "",
            template_id=payload.template_id,
            duration_seconds=payload.duration_seconds,
        )
        return result
    except Exception as exc:
        logger.error("Failed to generate recap script: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/auto-edit")
async def api_auto_edit(payload: AutoEditRequest) -> Dict[str, Any]:
    """
    Auto-cut scenes, synthesize voiceover, burn Burmese subtitles, and render output video.
    """
    try:
        render_result = simulate_auto_video_edit(
            recap_data=payload.recap_script,
            aspect_ratio=payload.aspect_ratio,
            subtitle_style=payload.subtitle_style,
        )
        return render_result
    except Exception as exc:
        logger.error("Failed to execute auto-edit pipeline: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
