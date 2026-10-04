"""Add scheduled processing retries and durable failed-job records.

Revision ID: 0004_processing_retry_dlq
Revises: 0003_scene_script_scope
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0004_processing_retry_dlq"
down_revision = "0003_scene_script_scope"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    job_columns = {column["name"] for column in inspector.get_columns("processing_jobs")}
    if "max_retries" not in job_columns:
        op.add_column(
            "processing_jobs",
            sa.Column("max_retries", sa.Integer(), server_default="3", nullable=False),
        )
    if "next_run_at" not in job_columns:
        op.add_column(
            "processing_jobs",
            sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        )
    if "last_error" not in job_columns:
        op.add_column("processing_jobs", sa.Column("last_error", sa.Text(), nullable=True))

    if "failed_jobs" not in inspector.get_table_names():
        op.create_table(
            "failed_jobs",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("processing_job_id", sa.String(length=36), nullable=False),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("retry_count", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("dlq_published_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["processing_job_id"], ["processing_jobs.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    index_names = {index["name"] for index in inspect(bind).get_indexes("processing_jobs")}
    if "ix_processing_jobs_dispatch_due" not in index_names:
        op.create_index(
            "ix_processing_jobs_dispatch_due",
            "processing_jobs",
            ["job_type", "status", "next_run_at"],
            unique=False,
        )

    failed_indexes = {index["name"] for index in inspect(bind).get_indexes("failed_jobs")}
    if "uq_failed_jobs_active_processing_job" not in failed_indexes:
        op.create_index(
            "uq_failed_jobs_active_processing_job",
            "failed_jobs",
            ["processing_job_id"],
            unique=True,
            postgresql_where=sa.text("resolved_at IS NULL"),
            sqlite_where=sa.text("resolved_at IS NULL"),
        )
    if "ix_failed_jobs_dlq_pending" not in failed_indexes:
        op.create_index(
            "ix_failed_jobs_dlq_pending",
            "failed_jobs",
            ["resolved_at", "dlq_published_at"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "failed_jobs" in inspector.get_table_names():
        for index in ("uq_failed_jobs_active_processing_job", "ix_failed_jobs_dlq_pending"):
            if index in {item["name"] for item in inspect(bind).get_indexes("failed_jobs")}:
                op.drop_index(index, table_name="failed_jobs")
        op.drop_table("failed_jobs")

    job_columns = {column["name"] for column in inspect(bind).get_columns("processing_jobs")}
    if "ix_processing_jobs_dispatch_due" in {
        index["name"] for index in inspect(bind).get_indexes("processing_jobs")
    }:
        op.drop_index("ix_processing_jobs_dispatch_due", table_name="processing_jobs")
    for column in ("last_error", "next_run_at", "max_retries"):
        if column in job_columns:
            op.drop_column("processing_jobs", column)
