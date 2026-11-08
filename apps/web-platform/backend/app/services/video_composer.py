"""Multi-Track Hybrid Video Composer for Narrativ Forge.

Enables assembling external AI video clips (Runway, Kling, Luma Dream Machine, Sora, Pika)
with multi-track dubbing, BGM auto-ducking, SFX, and dynamic anime-styled subtitles.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TransitionType(str, Enum):
    CUT = "cut"
    FADE_TO_BLACK = "fade_to_black"
    CROSS_DISSOLVE = "cross_dissolve"
    WHIP_PAN = "whip_pan"
    ANIME_FLASH = "anime_flash"


class VideoSourceProvider(str, Enum):
    RUNWAY_GEN3 = "runway_gen3"
    KLING_AI = "kling_ai"
    LUMA_DREAM = "luma_dream_machine"
    OPENAI_SORA = "openai_sora"
    PIKA = "pika_labs"
    LOCAL_UPLOAD = "local_upload"
    CUSTOM_URL = "custom_url"


@dataclass
class VideoClip:
    id: str
    source_url: str
    provider: VideoSourceProvider
    title: str
    start_trim_seconds: float = 0.0
    duration_seconds: float = 5.0
    speed_factor: float = 1.0
    transition_in: TransitionType = TransitionType.CUT
    transition_duration_seconds: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_url": self.source_url,
            "provider": self.provider.value,
            "title": self.title,
            "start_trim_seconds": self.start_trim_seconds,
            "duration_seconds": self.duration_seconds,
            "effective_duration_seconds": round(self.duration_seconds / max(self.speed_factor, 0.1), 2),
            "speed_factor": self.speed_factor,
            "transition_in": self.transition_in.value,
            "transition_duration_seconds": self.transition_duration_seconds,
        }


@dataclass
class AudioTrackCue:
    id: str
    track_type: str  # "dubbing", "bgm", "sfx"
    audio_url: str
    start_time_seconds: float
    duration_seconds: float
    volume_percent: float = 100.0
    auto_duck_on_speech: bool = False
    voice_binding: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "track_type": self.track_type,
            "audio_url": self.audio_url,
            "start_time_seconds": self.start_time_seconds,
            "duration_seconds": self.duration_seconds,
            "volume_percent": self.volume_percent,
            "auto_duck_on_speech": self.auto_duck_on_speech,
            "voice_binding": self.voice_binding,
        }


@dataclass
class SubtitleCue:
    id: str
    text: str
    start_time_seconds: float
    end_time_seconds: float
    speaker: Optional[str] = None
    style: str = "anime_pop"  # "anime_pop", "cinematic_bold", "classic_yellow", "minimal_white"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "start_time_seconds": self.start_time_seconds,
            "end_time_seconds": self.end_time_seconds,
            "duration_seconds": round(self.end_time_seconds - self.start_time_seconds, 2),
            "speaker": self.speaker,
            "style": self.style,
        }


class VideoComposerService:
    """Service for assembling multi-track timelines and exporting video jobs."""

    @classmethod
    def register_external_clip(
        cls,
        source_url: str,
        provider: VideoSourceProvider,
        title: str,
        duration_seconds: float = 5.0,
    ) -> Dict[str, Any]:
        """Validate and create metadata for an external AI video clip."""
        clip_id = f"clip_{uuid.uuid4().hex[:8]}"
        clip = VideoClip(
            id=clip_id,
            source_url=source_url,
            provider=provider,
            title=title,
            duration_seconds=duration_seconds,
        )
        return clip.to_dict()

    @classmethod
    def build_timeline(
        cls,
        title: str,
        video_clips: List[Dict[str, Any]],
        dubbing_cues: Optional[List[Dict[str, Any]]] = None,
        bgm_track_url: Optional[str] = None,
        bgm_volume_percent: float = 30.0,
        sfx_cues: Optional[List[Dict[str, Any]]] = None,
        subtitles: Optional[List[Dict[str, Any]]] = None,
        target_aspect_ratio: str = "9:16",
    ) -> Dict[str, Any]:
        """Assemble all tracks into an aligned timeline ready for rendering."""
        timeline_id = f"tl_{uuid.uuid4().hex[:8]}"

        # Calculate video sequence timings
        processed_video_track = []
        current_video_time = 0.0

        for raw_clip in video_clips:
            duration = float(raw_clip.get("duration_seconds", 5.0))
            speed = float(raw_clip.get("speed_factor", 1.0))
            effective_duration = round(duration / max(speed, 0.1), 2)

            clip_entry = {
                **raw_clip,
                "timeline_start": round(current_video_time, 2),
                "timeline_end": round(current_video_time + effective_duration, 2),
                "effective_duration": effective_duration,
            }
            processed_video_track.append(clip_entry)
            current_video_time += effective_duration

        total_video_duration = round(current_video_time, 2)

        # Assemble BGM Track
        audio_tracks = []
        if bgm_track_url:
            audio_tracks.append({
                "id": f"bgm_{uuid.uuid4().hex[:6]}",
                "track_type": "bgm",
                "audio_url": bgm_track_url,
                "start_time_seconds": 0.0,
                "duration_seconds": total_video_duration,
                "volume_percent": bgm_volume_percent,
                "auto_duck_on_speech": True,
            })

        # Assemble Dubbing Cues
        if dubbing_cues:
            for cue in dubbing_cues:
                audio_tracks.append({
                    "id": cue.get("id", f"dub_{uuid.uuid4().hex[:6]}"),
                    "track_type": "dubbing",
                    "audio_url": cue.get("audio_url", ""),
                    "start_time_seconds": cue.get("start_time_seconds", 0.0),
                    "duration_seconds": cue.get("duration_seconds", 2.0),
                    "volume_percent": cue.get("volume_percent", 100.0),
                    "voice_binding": cue.get("voice_binding"),
                })

        # Assemble SFX Cues
        if sfx_cues:
            for sfx in sfx_cues:
                audio_tracks.append({
                    "id": sfx.get("id", f"sfx_{uuid.uuid4().hex[:6]}"),
                    "track_type": "sfx",
                    "audio_url": sfx.get("audio_url", ""),
                    "start_time_seconds": sfx.get("start_time_seconds", 0.0),
                    "duration_seconds": sfx.get("duration_seconds", 1.0),
                    "volume_percent": sfx.get("volume_percent", 90.0),
                })

        # Assemble Subtitle Track
        processed_subtitles = subtitles or []

        return {
            "timeline_id": timeline_id,
            "title": title,
            "aspect_ratio": target_aspect_ratio,
            "total_duration_seconds": total_video_duration,
            "tracks": {
                "video": processed_video_track,
                "audio": audio_tracks,
                "subtitles": processed_subtitles,
            },
            "status": "ready_for_render",
            "render_preset": {
                "resolution": "1080x1920" if target_aspect_ratio == "9:16" else "1920x1080",
                "fps": 30,
                "audio_bitrate": "192k",
                "video_codec": "libx264",
            },
        }
