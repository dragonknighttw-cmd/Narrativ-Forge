"""Persist release evidence, provider acceptance, billing reconciliation, and launch-watch records.

Revision ID: 0017_release_maturity
Revises: 0017_asset_deleted_at
"""

from alembic import op
import sqlalchemy as sa


revision = "0017_release_maturity"
down_revision = "0017_asset_deleted_at"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evidence_ledger_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("gate", sa.String(80), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("commit_sha", sa.String(40), nullable=False),
        sa.Column("workflow_run", sa.String(255), nullable=False, server_default=""),
        sa.Column("evidence_ref", sa.String(1024), nullable=False, server_default=""),
        sa.Column("owner", sa.String(255), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("waiver_ref", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("gate", "commit_sha", name="uq_evidence_gate_commit"),
        sa.CheckConstraint("status IN ('pending', 'blocked', 'verified', 'waived')", name="ck_evidence_status"),
        sa.CheckConstraint(
            "(status <> 'verified') OR (workflow_run <> '' AND evidence_ref <> '' AND verified_at IS NOT NULL)",
            name="ck_evidence_verified_requires_proof",
        ),
        sa.CheckConstraint(
            "(status <> 'waived') OR (waiver_ref IS NOT NULL AND waiver_ref <> '')",
            name="ck_evidence_waived_requires_ref",
        ),
    )
    op.create_index("ix_evidence_ledger_gate", "evidence_ledger_entries", ["gate"])
    op.create_index("ix_evidence_ledger_status", "evidence_ledger_entries", ["status"])

    op.create_table(
        "provider_acceptance_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider", sa.String(80), nullable=False),
        sa.Column("credential_dependency", sa.String(255), nullable=False),
        sa.Column("quota_terms_review", sa.String(40), nullable=False, server_default="pending"),
        sa.Column("live_test_result", sa.String(40), nullable=False, server_default="pending"),
        sa.Column("fallback", sa.Text, nullable=False, server_default=""),
        sa.Column("commercial_use", sa.String(40), nullable=False, server_default="pending"),
        sa.Column("owner", sa.String(255), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("provider", name="uq_provider_acceptance_provider"),
    )

    op.create_table(
        "billing_reconciliation_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_key", sa.String(255), nullable=False),
        sa.Column("plan_state", sa.String(80), nullable=False),
        sa.Column("quota_units", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("reserved_units", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("usage_units", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("webhook_event_id", sa.String(255), nullable=False),
        sa.Column("webhook_status", sa.String(40), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
        sa.Column("failure_state", sa.String(80), nullable=False, server_default="none"),
        sa.Column("reconciled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("webhook_event_id", name="uq_billing_webhook_event"),
        sa.UniqueConstraint("tenant_key", "idempotency_key", name="uq_billing_tenant_idempotency"),
        sa.CheckConstraint(
            "quota_units >= 0 AND reserved_units >= 0 AND usage_units >= 0",
            name="ck_billing_nonnegative_units",
        ),
    )

    op.create_table(
        "release_candidates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("version", sa.String(80), nullable=False),
        sa.Column("commit_sha", sa.String(40), nullable=False),
        sa.Column("migration_plan_ref", sa.String(1024), nullable=False),
        sa.Column("environment_manifest_ref", sa.String(1024), nullable=False),
        sa.Column("rollback_ref", sa.String(1024), nullable=False),
        sa.Column("evidence_ledger_ref", sa.String(1024), nullable=False),
        sa.Column("acceptance_checklist_ref", sa.String(1024), nullable=False),
        sa.Column("frozen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("version", name="uq_release_candidate_version"),
    )

    op.create_table(
        "launch_watch_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("candidate_version", sa.String(80), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("severity", sa.String(40), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("rollback_decision", sa.String(40), nullable=False, server_default="none"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("launch_watch_events")
    op.drop_table("release_candidates")
    op.drop_table("billing_reconciliation_records")
    op.drop_table("provider_acceptance_records")
    op.drop_index("ix_evidence_ledger_status", table_name="evidence_ledger_entries")
    op.drop_index("ix_evidence_ledger_gate", table_name="evidence_ledger_entries")
    op.drop_table("evidence_ledger_entries")
