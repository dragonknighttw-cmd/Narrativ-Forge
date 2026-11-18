from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


def now() -> datetime:
    return datetime.now(timezone.utc)


class ReferenceVideo(Base):
    """
    Module 1: Reference Intelligence Engine
    Stores uploaded reference videos with extracted cinematic profiles
    (camera angles, pacing, color palette, lighting, music rhythm, storytelling).
    """
    __tablename__ = "reference_videos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)

    # Intelligence & Analysis JSON fields
    shot_count: Mapped[int] = mapped_column(Integer, default=0)
    pacing_cuts_per_minute: Mapped[float] = mapped_column(Float, default=0.0)
    style_tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    camera_movement_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    color_palette: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON hex codes & grade
    lighting_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)
    music_rhythm_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON BPM, beats
    storytelling_structure: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON 3-act / hook breakdown

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now, nullable=False)


class RawFootage(Base):
    """
    Module 2: Raw Footage Intelligence Engine
    Stores uploaded raw video B-roll/shots with automated scene detection,
    quality scoring, blur detection, object/action tags, and best shot highlights.
    """
    __tablename__ = "raw_footages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    resolution: Mapped[str] = mapped_column(String(50), default="1080x1920")
    fps: Mapped[float] = mapped_column(Float, default=30.0)

    # Intelligent Analysis
    quality_score: Mapped[float] = mapped_column(Float, default=85.0)  # 0 to 100
    stability_score: Mapped[float] = mapped_column(Float, default=80.0)  # 0 to 100
    blur_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    camera_movement: Mapped[str] = mapped_column(String(50), default="static")  # pan, tilt, zoom, static, shaky
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of tags
    is_b_roll: Mapped[bool] = mapped_column(Boolean, default=True)
    selected_highlight: Mapped[bool] = mapped_column(Boolean, default=False)

    # Detected Sub-Scenes
    scenes_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array of scene slices

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now, nullable=False)


class CreativeDirectorConcept(Base):
    """
    Module 3: AI Creative Director Engine
    Synthesizes multiple creative concepts:
    - Epic Cinematic Version
    - Fast-Paced Social Media Version (9:16)
    - Emotional Storytelling Version
    """
    __tablename__ = "creative_concepts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    episode_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    concept_type: Mapped[str] = mapped_column(String(50), default="epic_cinematic")  # epic_cinematic, fast_paced_social, emotional_storytelling
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    logline: Mapped[str] = mapped_column(Text, nullable=False)
    target_duration_seconds: Mapped[int] = mapped_column(Integer, default=180)  # 3 minutes default

    pacing_profile: Mapped[str] = mapped_column(String(100), default="Dynamic Action (2.5s - 3.8s / cut)")
    recommended_bgm_genre: Mapped[str] = mapped_column(String(100), default="Epic Orchestral")
    emotional_arc: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    shot_decisions: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON explanation of why shots were chosen
    status: Mapped[str] = mapped_column(String(30), default="draft")  # draft, approved, applied

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class MusicScoreAsset(Base):
    """
    Module 5: AI Music Intelligence & Generation Engine
    Epic Orchestral, Battle / War, Dark Fantasy, Phonk / Electronic, Ambient
    """
    __tablename__ = "music_score_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    genre: Mapped[str] = mapped_column(String(50), default="epic_orchestral")
    mood: Mapped[str] = mapped_column(String(100), default="Heroic, Tense")
    bpm: Mapped[int] = mapped_column(Integer, default=120)
    duration_seconds: Mapped[float] = mapped_column(Float, default=180.0)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)

    beat_grid_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list of beat timestamps
    beat_drops_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list of drop timestamps
    license_type: Mapped[str] = mapped_column(String(50), default="royalty_free")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class SoundDesignAsset(Base):
    """
    Module 6: Cinematic Sound Design Engine
    Impacts, Whooshes, Risers, Ambient Drones, Action Foley
    """
    __tablename__ = "sound_design_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="cinematic_impact")  # whoosh_transition, riser_buildup, ambient_drone, action_foley
    duration_seconds: Mapped[float] = mapped_column(Float, default=2.5)
    file_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    ducking_db: Mapped[float] = mapped_column(Float, default=-14.0)
    tags: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


class TimelineProject(Base):
    """
    Module 7: Advanced Multi-Track Timeline & Preview Engine
    Tracks: Video, B-roll, Narration, BGM, SFX, Subtitles
    """
    __tablename__ = "timeline_projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True, index=True)
    episode_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_aspect_ratio: Mapped[str] = mapped_column(String(10), default="9:16")

    # Full Multi-Track JSON representation
    tracks_json: Mapped[str] = mapped_column(Text, default="{}")
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    render_status: Mapped[str] = mapped_column(String(30), default="draft")  # draft, queued, rendering, rendered, failed
    final_video_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now, nullable=False)


class QualityControlReport(Base):
    """
    Module 8: Quality Control & Final Optimization Engine
    Validates Black frames, frozen frames, audio clipping, A/V sync, subtitle alignment.
    """
    __tablename__ = "quality_control_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    timeline_id: Mapped[str] = mapped_column(ForeignKey("timeline_projects.id", ondelete="CASCADE"), nullable=False, index=True)

    overall_score: Mapped[int] = mapped_column(Integer, default=95)  # 0 to 100
    black_frames_detected: Mapped[int] = mapped_column(Integer, default=0)
    frozen_frames_detected: Mapped[int] = mapped_column(Integer, default=0)
    audio_clipping_events: Mapped[int] = mapped_column(Integer, default=0)
    av_sync_offset_ms: Mapped[float] = mapped_column(Float, default=0.0)
    subtitle_sync_status: Mapped[str] = mapped_column(String(30), default="perfect")
    passed: Mapped[bool] = mapped_column(Boolean, default=True)
    issues_json: Mapped[str | None] = mapped_column(Text, nullable=True)  # Detailed issue markers

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
