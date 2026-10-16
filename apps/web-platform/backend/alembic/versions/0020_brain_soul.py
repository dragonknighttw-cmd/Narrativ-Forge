"""Add brain soul tables to Narrativ Forge

Revision ID: 0020_brain_soul
Revises: 0019_series_bible
Create Date: 2026-10-15
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "0020_brain_soul"
down_revision: Union[str, Sequence[str], None] = "0019_series_bible"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    # The bootstrap baseline imports all ORM models and may already have made
    # these tables. Keep this revision safe for both fresh and existing databases.
    if "brain_soul_context" not in tables:
        op.create_table(
            "brain_soul_context",
            sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
            sa.Column("context_key", sa.String(length=120), nullable=False),
            sa.Column("context_value", sa.Text(), nullable=False),
            sa.Column("description", sa.String(length=500), nullable=False, server_default=""),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("updated_by", sa.String(length=40), nullable=False, server_default="system"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("context_key", name="uq_brain_soul_context_key"),
        )
    context_indexes = {item["name"] for item in inspect(bind).get_indexes("brain_soul_context")}
    if "ix_brain_soul_context_key" not in context_indexes:
        op.create_index("ix_brain_soul_context_key", "brain_soul_context", ["context_key"], unique=True)
    if "ix_brain_soul_context_active" not in context_indexes:
        op.create_index("ix_brain_soul_context_active", "brain_soul_context", ["is_active"])

    # ── brain_soul_syntheses (weekly LLM story/content snapshot) ─────────────
    if "brain_soul_syntheses" not in set(inspect(bind).get_table_names()):
        op.create_table(
            "brain_soul_syntheses",
            sa.Column("id", sa.Integer(), nullable=False, autoincrement=True),
            sa.Column("period_label", sa.String(length=40), nullable=False),
            sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
            sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
            sa.Column("topic", sa.String(length=80), nullable=False, server_default="story"),
            sa.Column("synthesis_text", sa.Text(), nullable=False),
            sa.Column("source_item_ids", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("item_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("provider", sa.String(length=120), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("period_label", "topic", name="uq_brain_soul_synth_period_topic"),
        )
    synth_indexes = {item["name"] for item in inspect(bind).get_indexes("brain_soul_syntheses")}
    if "ix_brain_soul_synth_period" not in synth_indexes:
        op.create_index("ix_brain_soul_synth_period", "brain_soul_syntheses", ["period_label"])
    if "ix_brain_soul_synth_topic" not in synth_indexes:
        op.create_index("ix_brain_soul_synth_topic", "brain_soul_syntheses", ["topic"])
    if "ix_brain_soul_synth_created" not in synth_indexes:
        op.create_index("ix_brain_soul_synth_created", "brain_soul_syntheses", ["created_at"])


def downgrade() -> None:
    # Revision 0001_bootstrap imports the current ORM metadata and may have
    # created these tables before this revision ran. Their ownership cannot be
    # inferred safely, so retain the tables rather than risk deleting user data.
    # This is intentionally non-destructive; a downgrade does not remove this
    # revision's tables when the baseline may own them.
    return
