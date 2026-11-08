from __future__ import annotations

import io
import edge_tts
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field

from ...services.manga_engine import (
    MangaEngine,
    LayoutType,
    MANGA_SFX_CATALOG,
)

router = APIRouter(prefix="/manga", tags=["manga-webtoon-studio"])


class BubbleVoiceRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    voice: str = Field(default="ja-JP-NanamiNeural")


class MangaGenerateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    story_synopsis: str = Field(min_length=5, max_length=5000)
    layout_type: LayoutType = Field(default=LayoutType.WEBTOON_VERTICAL)
    anime_style_prompt: Optional[str] = Field(
        default="anime style, makoto shinkai aesthetic, high contrast manga inks, crisp lineart"
    )
    characters: Optional[List[str]] = Field(default_factory=lambda: ["Protagonist", "Rival"])


class MotionComicExportRequest(BaseModel):
    manga_page: Dict[str, Any]
    bgm_track: Optional[str] = "anime_cinematic_bgm.mp3"


@router.get("/templates")
def list_manga_templates():
    """Return available Manga and Webtoon layout templates."""
    return MangaEngine.get_layout_templates()


@router.get("/sfx-catalog")
def list_sfx_catalog():
    """Return curated Manga Onomatopoeia / SFX library with Japanese and Burmese sounds."""
    return MANGA_SFX_CATALOG


@router.post("/generate")
def generate_manga_storyboard(payload: MangaGenerateRequest):
    """Generate multi-panel layout, visual prompts, and speech bubbles for a scene."""
    page = MangaEngine.generate_manga_page(
        title=payload.title,
        story_synopsis=payload.story_synopsis,
        layout_type=payload.layout_type,
        anime_style_prompt=payload.anime_style_prompt,
        character_names=payload.characters,
    )
    return page


@router.post("/motion-comic/export")
def export_motion_comic(payload: MotionComicExportRequest):
    """Compile a manga page into an animated Motion Comic video timeline."""
    timeline = MangaEngine.compile_motion_comic_timeline(
        manga_page=payload.manga_page,
        bgm_track=payload.bgm_track,
    )
    return timeline


@router.post("/synthesize-bubble-voice")
async def synthesize_bubble_voice(payload: BubbleVoiceRequest):
    """Generate audio stream for dialogue bubble using Edge-TTS."""
    try:
        communicate = edge_tts.Communicate(text=payload.text, voice=payload.voice)
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        audio_bytes = audio_stream.getvalue()
        if not audio_bytes:
            raise HTTPException(status_code=500, detail="Voice synthesis failed")
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=bubble.mp3"},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
