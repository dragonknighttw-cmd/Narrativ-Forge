from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


def now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(40), default="owner")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Idea(Base):
    __tablename__ = "ideas"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255))
    concept: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hook: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_warning: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="idea")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Series(Base):
    __tablename__ = "series"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = (UniqueConstraint("series_id", "season_number", name="uq_season_number_per_series"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    series_id: Mapped[str] = mapped_column(ForeignKey("series.id"), index=True)
    season_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Episode(Base):
    __tablename__ = "episodes"
    __table_args__ = (UniqueConstraint("season_id", "episode_number", name="uq_episode_number_per_season"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    public_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    series_id: Mapped[str] = mapped_column(ForeignKey("series.id"), index=True)
    season_id: Mapped[str | None] = mapped_column(ForeignKey("seasons.id"), nullable=True)
    episode_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    synopsis: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_duration_seconds: Mapped[int] = mapped_column(Integer, default=180)
    actual_duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="idea")
    current_step: Mapped[str] = mapped_column(String(40), default="idea")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Script(Base):
    __tablename__ = "scripts"
    __table_args__ = (UniqueConstraint("episode_id", "version", name="uq_script_version_per_episode"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="draft")
    is_current: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class Scene(Base):
    __tablename__ = "scenes"
    __table_args__ = (UniqueConstraint("episode_id", "scene_number", name="uq_scene_number_per_episode"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    script_id: Mapped[str | None] = mapped_column(ForeignKey("scripts.id"), nullable=True)
    scene_number: Mapped[int] = mapped_column(Integer)
    purpose: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    dialogue: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    job_type: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default="queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    input_asset_id: Mapped[str | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    output_asset_id: Mapped[str | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint("episode_id", "version", name="uq_asset_version_per_episode"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    scene_id: Mapped[str | None] = mapped_column(ForeignKey("scenes.id"), nullable=True, index=True)
    asset_type: Mapped[str] = mapped_column(String(40))
    original_filename: Mapped[str] = mapped_column(String(255))
    storage_provider: Mapped[str] = mapped_column(String(40), default="local")
    local_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    drive_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100))
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    copyright_status: Mapped[str] = mapped_column(String(40), default="unknown")
    version: Mapped[int] = mapped_column(Integer)
    is_final: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String(40), default="uploaded")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Subtitle(Base):
    __tablename__ = "subtitles"
    __table_args__ = (UniqueConstraint("episode_id", "version", name="uq_subtitle_version_per_episode"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    language: Mapped[str] = mapped_column(String(10), default="my")
    format: Mapped[str] = mapped_column(String(10), default="srt")
    preset: Mapped[str] = mapped_column(String(40), default="burmese_default")
    cues_json: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(String(40), default="draft")
    is_current: Mapped[bool] = mapped_column(default=True)
    validation_errors_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class ExportRecord(Base):
    __tablename__ = "export_records"
    __table_args__ = (UniqueConstraint("episode_id", "provider", name="uq_export_episode_provider"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    provider: Mapped[str] = mapped_column(String(40), default="mock_drive")
    status: Mapped[str] = mapped_column(String(40), default="queued")
    manifest_json: Mapped[str] = mapped_column(Text, default="{}")
    drive_folder_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    drive_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class GoogleDriveConnection(Base):
    __tablename__ = "google_drive_connections"
    __table_args__ = (UniqueConstraint("user_email", name="uq_google_drive_user"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_email: Mapped[str] = mapped_column(String(255), index=True)
    refresh_token_encrypted: Mapped[str] = mapped_column(Text)
    access_token_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scope: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class ReviewRecord(Base):
    __tablename__ = "review_records"
    __table_args__ = (UniqueConstraint("episode_id", name="uq_review_episode"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    checklist_json: Mapped[str] = mapped_column(Text, default="{}")
    critical_issues_json: Mapped[str] = mapped_column(Text, default="[]")
    notes: Mapped[str] = mapped_column(Text, default="")
    decision: Mapped[str] = mapped_column(String(40), default="pending")
    revision_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class HookLibrary(Base):
    __tablename__ = "hook_library"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    hook_text: Mapped[str] = mapped_column(Text)
    hook_type: Mapped[str] = mapped_column(String(40))
    topic: Mapped[str | None] = mapped_column(String(100), nullable=True)
    emotion: Mapped[str | None] = mapped_column(String(100), nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    views_average: Mapped[float | None] = mapped_column(default=None)
    completion_average: Mapped[float | None] = mapped_column(default=None)
    shares_average: Mapped[float | None] = mapped_column(default=None)
    performance_score: Mapped[float | None] = mapped_column(default=None)
    is_default: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class ManualProductionLog(Base):
    __tablename__ = "manual_production_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    episode_id: Mapped[str | None] = mapped_column(ForeignKey("episodes.id"), nullable=True, index=True)
    topic: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hook: Mapped[str | None] = mapped_column(Text, nullable=True)
    hook_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    script_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scene_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    voice_tool: Mapped[str | None] = mapped_column(String(100), nullable=True)
    image_tool: Mapped[str | None] = mapped_column(String(100), nullable=True)
    video_tool: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subtitle_style: Mapped[str | None] = mapped_column(String(100), nullable=True)
    production_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    manual_errors: Mapped[str | None] = mapped_column(Text, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(default=None)
    published: Mapped[bool] = mapped_column(default=False)
    platform: Mapped[str | None] = mapped_column(String(40), nullable=True)
    views: Mapped[int | None] = mapped_column(Integer, nullable=True)
    watch_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_rate: Mapped[float | None] = mapped_column(default=None)
    shares: Mapped[int | None] = mapped_column(Integer, nullable=True)
    saves: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class SocialPublication(Base):
    __tablename__ = "social_publications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    platform: Mapped[str] = mapped_column(String(40))
    state: Mapped[str] = mapped_column(String(40), default="not_ready")
    caption: Mapped[str] = mapped_column(Text, default="")
    hashtags_json: Mapped[str] = mapped_column(Text, default="[]")
    schedule_metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    platform_format_valid: Mapped[bool] = mapped_column(default=False)
    publish_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class SocialAnalyticsRecord(Base):
    __tablename__ = "social_analytics_records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    publication_id: Mapped[str] = mapped_column(ForeignKey("social_publications.id"), index=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    watch_time_seconds: Mapped[int] = mapped_column(Integer, default=0)
    completion_rate: Mapped[float] = mapped_column(default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    saves: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(40), default="manual")
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
