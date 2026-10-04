from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base


def now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(40), default="viewer")
    password_hash: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (
        UniqueConstraint("actor_id", "key", name="uq_idempotency_actor_key"),
        CheckConstraint("status IN ('processing', 'completed')", name="ck_idempotency_status"),
        Index("ix_idempotency_records_expires_at", "expires_at"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    target: Mapped[str] = mapped_column(String(1024), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="processing")
    resource_type: Mapped[str] = mapped_column(String(40), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False)
    response_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


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

    seasons: Mapped[list[Season]] = relationship(back_populates="series")
    episodes: Mapped[list[Episode]] = relationship(back_populates="series")


class Season(Base):
    __tablename__ = "seasons"
    __table_args__ = (UniqueConstraint("series_id", "season_number", name="uq_season_number_per_series"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    series_id: Mapped[str] = mapped_column(ForeignKey("series.id"), index=True)
    season_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    series: Mapped[Series] = relationship(back_populates="seasons")
    episodes: Mapped[list[Episode]] = relationship(back_populates="season")


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
    row_version: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"), nullable=False)

    series: Mapped[Series] = relationship(back_populates="episodes")
    season: Mapped[Season | None] = relationship(back_populates="episodes")
    scripts: Mapped[list[Script]] = relationship(back_populates="episode")
    scenes: Mapped[list[Scene]] = relationship(back_populates="episode")
    processing_jobs: Mapped[list[ProcessingJob]] = relationship(back_populates="episode")
    assets: Mapped[list[Asset]] = relationship(back_populates="episode")
    subtitles: Mapped[list[Subtitle]] = relationship(back_populates="episode")
    export_records: Mapped[list[ExportRecord]] = relationship(back_populates="episode")
    review_record: Mapped[ReviewRecord | None] = relationship(
        back_populates="episode",
        uselist=False,
    )
    manual_production_logs: Mapped[list[ManualProductionLog]] = relationship(back_populates="episode")
    social_publications: Mapped[list[SocialPublication]] = relationship(back_populates="episode")


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
    row_version: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"), nullable=False)

    episode: Mapped[Episode] = relationship(back_populates="scripts")
    scenes: Mapped[list[Scene]] = relationship(back_populates="script")


class Scene(Base):
    __tablename__ = "scenes"
    __table_args__ = (UniqueConstraint("script_id", "scene_number", name="uq_scene_number_per_script"),)
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

    episode: Mapped[Episode] = relationship(back_populates="scenes")
    script: Mapped[Script | None] = relationship(back_populates="scenes")
    assets: Mapped[list[Asset]] = relationship(back_populates="scene")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    __table_args__ = (
        Index("ix_processing_jobs_dispatch_due", "job_type", "status", "next_run_at"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), index=True)
    job_type: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), default="queued")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, server_default=text("3"), nullable=False)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_asset_id: Mapped[str | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    output_asset_id: Mapped[str | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

    episode: Mapped[Episode] = relationship(back_populates="processing_jobs")
    input_asset: Mapped[Asset | None] = relationship(
        foreign_keys=[input_asset_id],
        back_populates="input_jobs",
    )
    output_asset: Mapped[Asset | None] = relationship(
        foreign_keys=[output_asset_id],
        back_populates="output_jobs",
    )


class FailedJob(Base):
    __tablename__ = "failed_jobs"
    __table_args__ = (
        Index(
            "uq_failed_jobs_active_processing_job",
            "processing_job_id",
            unique=True,
            postgresql_where=text("resolved_at IS NULL"),
            sqlite_where=text("resolved_at IS NULL"),
        ),
        Index("ix_failed_jobs_dlq_pending", "resolved_at", "dlq_published_at"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    processing_job_id: Mapped[str] = mapped_column(
        ForeignKey("processing_jobs.id"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dlq_published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class UploadSession(Base):
    __tablename__ = "upload_sessions"
    __table_args__ = (
        UniqueConstraint("episode_id", "reserved_version", name="uq_upload_session_episode_version"),
        Index("ix_upload_sessions_owner_status_expiry", "owner_id", "status", "expires_at"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    episode_id: Mapped[str] = mapped_column(ForeignKey("episodes.id"), nullable=False)
    reserved_version: Mapped[int] = mapped_column(Integer, nullable=False)
    asset_type: Mapped[str] = mapped_column(String(40), nullable=False)
    scene_id: Mapped[str | None] = mapped_column(ForeignKey("scenes.id"), nullable=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    expected_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chunk_size: Mapped[int] = mapped_column(Integer, nullable=False)
    copyright_status: Mapped[str] = mapped_column(String(40), nullable=False, default="unknown")
    storage_provider: Mapped[str] = mapped_column(String(40), nullable=False)
    object_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    provider_upload_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UploadPart(Base):
    __tablename__ = "upload_parts"
    __table_args__ = (
        UniqueConstraint("upload_session_id", "part_number", name="uq_upload_part_number"),
        CheckConstraint("part_number BETWEEN 1 AND 10000", name="ck_upload_part_number_range"),
        CheckConstraint("size_bytes > 0", name="ck_upload_part_size_positive"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    upload_session_id: Mapped[str] = mapped_column(
        ForeignKey("upload_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    part_number: Mapped[int] = mapped_column(Integer, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_etag: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, nullable=False)


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
    object_key: Mapped[str | None] = mapped_column(String(1024), nullable=True, index=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
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

    episode: Mapped[Episode] = relationship(back_populates="assets")
    scene: Mapped[Scene | None] = relationship(back_populates="assets")
    input_jobs: Mapped[list[ProcessingJob]] = relationship(
        foreign_keys="ProcessingJob.input_asset_id",
        back_populates="input_asset",
    )
    output_jobs: Mapped[list[ProcessingJob]] = relationship(
        foreign_keys="ProcessingJob.output_asset_id",
        back_populates="output_asset",
    )


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

    episode: Mapped[Episode] = relationship(back_populates="subtitles")


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

    episode: Mapped[Episode] = relationship(back_populates="export_records")


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

    episode: Mapped[Episode] = relationship(back_populates="review_record")


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

    episode: Mapped[Episode | None] = relationship(back_populates="manual_production_logs")


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

    episode: Mapped[Episode] = relationship(back_populates="social_publications")
    analytics_records: Mapped[list[SocialAnalyticsRecord]] = relationship(back_populates="publication")


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

    publication: Mapped[SocialPublication] = relationship(back_populates="analytics_records")


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    actor_email: Mapped[str] = mapped_column(String(255), index=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    resource_type: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[str] = mapped_column(String(36), index=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
