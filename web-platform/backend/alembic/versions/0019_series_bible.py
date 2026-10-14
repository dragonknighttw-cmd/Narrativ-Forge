"""Persist the character and voice portion of each Series Bible.

Revision ID: 0019_series_bible
Revises: 0018_tenant_backfill_guard
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0019_series_bible"
down_revision = "0018_tenant_backfill_guard"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if not inspect(bind).has_table("series_bibles"):
        op.create_table(
            "series_bibles",
            sa.Column("id", sa.String(length=36), primary_key=True),
            sa.Column("organization_id", sa.String(length=36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
            sa.Column("series_id", sa.String(length=36), sa.ForeignKey("series.id", ondelete="CASCADE"), nullable=False),
            sa.Column("characters_json", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.UniqueConstraint("series_id", name="uq_series_bibles_series_id"),
        )
        op.create_index("ix_series_bibles_organization_id", "series_bibles", ["organization_id"])
        op.create_index("ix_series_bibles_series_id", "series_bibles", ["series_id"])


def downgrade() -> None:
    bind = op.get_bind()
    if inspect(bind).has_table("series_bibles"):
        op.drop_table("series_bibles")
