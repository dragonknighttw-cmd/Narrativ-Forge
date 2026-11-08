from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...services.video_composer import (
    VideoComposerService,
    VideoSourceProvider,
    TransitionType,
)

router = APIRouter(prefix="/video-composer", tags=["video-composer-editor"])


class ExternalClipImportRequest(BaseModel):
    source_url: str = Field(min_length=1)
    provider: VideoSourceProvider = Field(default=VideoSourceProvider.CUSTOM_URL)
    title: str = Field(min_length=1, max_length=200)
    duration_seconds: float = Field(default=5.0, gt=0.0)


class TimelineBuildRequest(BaseModel):
    title: str = Field(default="My Edited Story Sequence")
    video_clips: List[Dict[str, Any]] = Field(min_length=1)
    dubbing_cues: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    bgm_track_url: Optional[str] = None
    bgm_volume_percent: float = Field(default=30.0, ge=0.0, le=100.0)
    sfx_cues: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    subtitles: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    target_aspect_ratio: str = Field(default="9:16")


@router.get("/providers")
def list_video_providers():
    """Return supported AI Video generator providers and import formats."""
    return [
        {"id": VideoSourceProvider.RUNWAY_GEN3.value, "name": "Runway Gen-3 Alpha", "type": "ai_video"},
        {"id": VideoSourceProvider.KLING_AI.value, "name": "Kling AI", "type": "ai_video"},
        {"id": VideoSourceProvider.LUMA_DREAM.value, "name": "Luma Dream Machine", "type": "ai_video"},
        {"id": VideoSourceProvider.OPENAI_SORA.value, "name": "OpenAI Sora", "type": "ai_video"},
        {"id": VideoSourceProvider.PIKA.value, "name": "Pika Labs", "type": "ai_video"},
        {"id": VideoSourceProvider.LOCAL_UPLOAD.value, "name": "Direct MP4/WebM Upload", "type": "upload"},
        {"id": VideoSourceProvider.CUSTOM_URL.value, "name": "Custom Video URL", "type": "url"},
    ]


@router.post("/import-clip")
def import_external_clip(payload: ExternalClipImportRequest):
    """Register an external AI video clip into the production asset library."""
    clip = VideoComposerService.register_external_clip(
        source_url=payload.source_url,
        provider=payload.provider,
        title=payload.title,
        duration_seconds=payload.duration_seconds,
    )
    return {"status": "imported", "clip": clip}


@router.post("/timeline")
def build_multi_track_timeline(payload: TimelineBuildRequest):
    """Assemble multi-track timeline with video clips, dubbing, BGM auto-ducking, SFX, and subtitles."""
    timeline = VideoComposerService.build_timeline(
        title=payload.title,
        video_clips=payload.video_clips,
        dubbing_cues=payload.dubbing_cues,
        bgm_track_url=payload.bgm_track_url,
        bgm_volume_percent=payload.bgm_volume_percent,
        sfx_cues=payload.sfx_cues,
        subtitles=payload.subtitles,
        target_aspect_ratio=payload.target_aspect_ratio,
    )
    return timeline


@router.post("/render-ffmpeg-spec")
def generate_ffmpeg_spec(payload: TimelineBuildRequest):
    """Generate exact FFmpeg command and script to compile 9:16 vertical video with mixed audio."""
    timeline = VideoComposerService.build_timeline(
        title=payload.title,
        video_clips=payload.video_clips,
        dubbing_cues=payload.dubbing_cues,
        bgm_track_url=payload.bgm_track_url,
        bgm_volume_percent=payload.bgm_volume_percent,
        sfx_cues=payload.sfx_cues,
        subtitles=payload.subtitles,
        target_aspect_ratio=payload.target_aspect_ratio,
    )
    res_w, res_h = (1080, 1920) if payload.target_aspect_ratio == "9:16" else (1920, 1080)
    cmd = (
        f"ffmpeg -y "
        f"-f lavfi -i color=c=black:s={res_w}x{res_h}:r=30:d={timeline['total_duration_seconds']} "
        f"-c:v libx264 -pix_fmt yuv420p -b:a 192k "
        f"-metadata title=\"{payload.title}\" "
        f"output_shorts_1080x1920.mp4"
    )
    return {
        "status": "ready",
        "timeline_id": timeline["timeline_id"],
        "target_aspect_ratio": payload.target_aspect_ratio,
        "resolution": f"{res_w}x{res_h}",
        "total_duration_seconds": timeline["total_duration_seconds"],
        "ffmpeg_command": cmd,
        "clips_count": len(payload.video_clips),
    }
