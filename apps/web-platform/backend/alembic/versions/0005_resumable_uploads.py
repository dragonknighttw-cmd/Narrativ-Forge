"""Add persistent multipart upload sessions and part records."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0005_resumable_uploads"
down_revision = "0004_processing_retry_dlq"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    if "upload_sessions" not in tables:
        op.create_table(
            "upload_sessions",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("owner_id", sa.String(length=36), nullable=False),
            sa.Column("episode_id", sa.String(length=36), nullable=False),
            sa.Column("reserved_version", sa.Integer(), nullable=False),
            sa.Column("asset_type", sa.String(length=40), nullable=False),
            sa.Column("scene_id", sa.String(length=36), nullable=True),
            sa.Column("original_filename", sa.String(length=255), nullable=False),
            sa.Column("mime_type", sa.String(length=100), nullable=False),
            sa.Column("expected_size", sa.BigInteger(), nullable=False),
            sa.Column("chunk_size", sa.Integer(), nullable=False),
            sa.Column("copyright_status", sa.String(length=40), nullable=False),
            sa.Column("storage_provider", sa.String(length=40), nullable=False),
            sa.Column("object_key", sa.String(length=1024), nullable=False),
            sa.Column("provider_upload_id", sa.String(length=255), nullable=True),
            sa.Column("status", sa.String(length=40), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["episode_id"], ["episodes.id"]),
            sa.ForeignKeyConstraint(["scene_id"], ["scenes.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "episode_id",
                "reserved_version",
                name="uq_upload_session_episode_version",
            ),
        )
    if "upload_parts" not in tables:
        op.create_table(
            "upload_parts",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("upload_session_id", sa.String(length=36), nullable=False),
            sa.Column("part_number", sa.Integer(), nullable=False),
            sa.Column("size_bytes", sa.BigInteger(), nullable=False),
            sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
            sa.Column("provider_etag", sa.String(length=255), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.CheckConstraint(
                "part_number BETWEEN 1 AND 10000",
                name="ck_upload_part_number_range",
            ),
            sa.CheckConstraint("size_bytes > 0", name="ck_upload_part_size_positive"),
            sa.ForeignKeyConstraint(
                ["upload_session_id"],
                ["upload_sessions.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "upload_session_id",
                "part_number",
                name="uq_upload_part_number",
            ),
        )

    indexes = {index["name"] for index in inspect(bind).get_indexes("upload_sessions")}
    if "ix_upload_sessions_owner_status_expiry" not in indexes:
        op.create_index(
            "ix_upload_sessions_owner_status_expiry",
            "upload_sessions",
            ["owner_id", "status", "expires_at"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())
    if "upload_parts" in tables:
        op.drop_table("upload_parts")
    if "upload_sessions" in tables:
        indexes = {index["name"] for index in inspect(bind).get_indexes("upload_sessions")}
        if "ix_upload_sessions_owner_status_expiry" in indexes:
            op.drop_index("ix_upload_sessions_owner_status_expiry", table_name="upload_sessions")
        op.drop_table("upload_sessions")
