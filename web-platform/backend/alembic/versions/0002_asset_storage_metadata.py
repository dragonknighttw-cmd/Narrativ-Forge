"""add durable storage metadata to assets"""
from alembic import op
import sqlalchemy as sa

revision = "0002_asset_storage_metadata"
down_revision = "0001_bootstrap"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("object_key", sa.String(length=1024), nullable=True))
    op.add_column("assets", sa.Column("checksum_sha256", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("assets", "checksum_sha256")
    op.drop_column("assets", "object_key")
