"""Add asynchronous storage replica tracking for assets."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0008_storage_replicas"
down_revision = "0007_optimistic_locking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "storage_replicas" not in inspect(bind).get_table_names():
        op.create_table(
            "storage_replicas",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("asset_id", sa.String(length=36), nullable=False),
            sa.Column("provider", sa.String(length=40), nullable=False),
            sa.Column("object_key", sa.String(length=1024), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False, server_default="queued"),
            sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
            sa.Column("size_bytes", sa.BigInteger(), nullable=True),
            sa.Column("last_error", sa.Text(), nullable=True),
            sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("asset_id", "provider", name="uq_storage_replica_asset_provider"),
        )
        op.create_index("ix_storage_replicas_asset_id", "storage_replicas", ["asset_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    if "storage_replicas" in inspect(bind).get_table_names():
        if "ix_storage_replicas_asset_id" in {item["name"] for item in inspect(bind).get_indexes("storage_replicas")}:
            op.drop_index("ix_storage_replicas_asset_id", table_name="storage_replicas")
        op.drop_table("storage_replicas")
