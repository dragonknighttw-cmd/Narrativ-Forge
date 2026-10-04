"""Add actor-scoped idempotency response records."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0006_idempotency_keys"
down_revision = "0005_resumable_uploads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "idempotency_records" not in inspect(bind).get_table_names():
        op.create_table(
            "idempotency_records",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("actor_id", sa.String(length=36), nullable=False),
            sa.Column("key", sa.String(length=255), nullable=False),
            sa.Column("method", sa.String(length=10), nullable=False),
            sa.Column("target", sa.String(length=1024), nullable=False),
            sa.Column("request_fingerprint", sa.String(length=64), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("resource_type", sa.String(length=40), nullable=False),
            sa.Column("resource_id", sa.String(length=36), nullable=False),
            sa.Column("response_status", sa.Integer(), nullable=True),
            sa.Column("response_body", sa.Text(), nullable=True),
            sa.Column("response_content_type", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.CheckConstraint(
                "status IN ('processing', 'completed')",
                name="ck_idempotency_status",
            ),
            sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("actor_id", "key", name="uq_idempotency_actor_key"),
        )
    indexes = {item["name"] for item in inspect(bind).get_indexes("idempotency_records")}
    if "ix_idempotency_records_expires_at" not in indexes:
        op.create_index(
            "ix_idempotency_records_expires_at",
            "idempotency_records",
            ["expires_at"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    if "idempotency_records" in inspect(bind).get_table_names():
        if "ix_idempotency_records_expires_at" in {
            item["name"] for item in inspect(bind).get_indexes("idempotency_records")
        }:
            op.drop_index("ix_idempotency_records_expires_at", table_name="idempotency_records")
        op.drop_table("idempotency_records")
