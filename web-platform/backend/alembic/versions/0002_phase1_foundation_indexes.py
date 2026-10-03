"""add Phase 1 query indexes

Revision ID: 0002_phase1_foundation_indexes
Revises: 0001_bootstrap
"""
from alembic import op

revision = "0002_phase1_foundation_indexes"
down_revision = "0001_bootstrap"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_assets_checksum_sha256", "assets", ["checksum_sha256"], unique=False)
    op.create_index(
        "ix_processing_jobs_status_created_at",
        "processing_jobs",
        ["status", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_processing_jobs_status_created_at", table_name="processing_jobs")
    op.drop_index("ix_assets_checksum_sha256", table_name="assets")
