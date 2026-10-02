"""add durable storage metadata to assets"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002_asset_storage_metadata"
down_revision = "0001_bootstrap"
branch_labels = None
depends_on = None


def upgrade() -> None:
    inspector = inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("assets")}
    if "object_key" not in columns:
        op.add_column("assets", sa.Column("object_key", sa.String(length=1024), nullable=True))
    if "checksum_sha256" not in columns:
        op.add_column("assets", sa.Column("checksum_sha256", sa.String(length=64), nullable=True))


def downgrade() -> None:
    inspector = inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("assets")}
    if "checksum_sha256" in columns:
        op.drop_column("assets", "checksum_sha256")
    if "object_key" in columns:
        op.drop_column("assets", "object_key")
