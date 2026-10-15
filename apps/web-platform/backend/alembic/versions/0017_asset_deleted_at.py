"""Track asset soft-delete time for retention GC.

Revision ID: 0017_asset_deleted_at
Revises: 0016_scene_constraint_repair
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0017_asset_deleted_at"
down_revision = "0016_scene_constraint_repair"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in inspect(bind).get_columns("assets")}
    if "deleted_at" not in columns:
        op.add_column("assets", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in inspect(bind).get_columns("assets")}
    if "deleted_at" in columns:
        op.drop_column("assets", "deleted_at")
