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
