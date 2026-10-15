"""Brain Soul Layer models for Narrativ Forge.

Uses the same ``Base`` from ``app.db`` so ``Base.metadata.create_all``
picks these up automatically in development, and the Alembic migration
``0020_brain_soul.py`` handles production deployments.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class BrainSoulContext(Base):
    """Soul File — personal context key-value store for the operator."""

    __tablename__ = "brain_soul_context"
    __table_args__ = (
        UniqueConstraint("context_key", name="uq_brain_soul_context_key"),
        Index("ix_brain_soul_context_active", "is_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    context_key: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    context_value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    updated_by: Mapped[str] = mapped_column(String(40), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, onupdate=_now, server_default=func.now()
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "key": self.context_key,
            "value": self.context_value,
            "description": self.description,
            "is_active": self.is_active,
            "updated_by": self.updated_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class BrainSoulSynthesis(Base):
    """Weekly LLM synthesis snapshot for story/content patterns."""

    __tablename__ = "brain_soul_syntheses"
    __table_args__ = (
        UniqueConstraint("period_label", "topic", name="uq_brain_soul_synth_period_topic"),
        Index("ix_brain_soul_synth_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    period_label: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    topic: Mapped[str] = mapped_column(String(80), nullable=False, default="story", index=True)
    synthesis_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_item_ids: Mapped[str] = mapped_column(Text, nullable=False, default="[]")  # JSON list
    item_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    provider: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, server_default=func.now()
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "period_label": self.period_label,
            "period_start": self.period_start.isoformat() if self.period_start else None,
            "period_end": self.period_end.isoformat() if self.period_end else None,
            "topic": self.topic,
            "synthesis_text": self.synthesis_text,
            "source_item_ids": json.loads(self.source_item_ids or "[]"),
            "item_count": self.item_count,
            "provider": self.provider,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
