from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.core import (
    BillingReconciliationRecord,
    EvidenceLedgerEntry as EvidenceLedgerRow,
    LaunchWatchEventRecord,
    ProviderAcceptanceRecord,
    ReleaseCandidateRecord,
)
from app.services.release_maturity import (
    BillingReconciliation,
    EvidenceLedgerEntry,
    LaunchWatchEvent,
    ProviderAcceptance,
    ReleaseCandidate,
    validate_evidence_entry,
)


def upsert_evidence(session: Session, entry: EvidenceLedgerEntry) -> EvidenceLedgerRow:
    errors = validate_evidence_entry(entry)
    if errors:
        raise ValueError(",".join(errors))
    row = session.scalar(
        select(EvidenceLedgerRow).where(
            EvidenceLedgerRow.gate == entry.gate,
            EvidenceLedgerRow.commit_sha == entry.commit_sha,
        )
    )
    if row is None:
        row = EvidenceLedgerRow(id=str(uuid4()))
        session.add(row)
    row.gate = entry.gate
    row.status = entry.status
    row.commit_sha = entry.commit_sha
    row.workflow_run = entry.workflow_run
    row.evidence_ref = entry.evidence_ref
    row.owner = entry.owner
    row.verified_at = entry.verified_at
    row.waiver_ref = entry.waiver_ref
    session.flush()
    return row


def upsert_provider(session: Session, acceptance: ProviderAcceptance) -> ProviderAcceptanceRecord:
    row = session.scalar(
        select(ProviderAcceptanceRecord).where(
            ProviderAcceptanceRecord.provider == acceptance.provider
        )
    )
    if row is None:
        row = ProviderAcceptanceRecord(id=str(uuid4()))
        session.add(row)
    row.provider = acceptance.provider
    row.credential_dependency = acceptance.credential_dependency
    row.quota_terms_review = acceptance.quota_terms_review
    row.live_test_result = acceptance.live_test_result
    row.fallback = acceptance.fallback
    row.commercial_use = acceptance.commercial_use
    row.owner = acceptance.owner
    row.accepted_at = acceptance.accepted_at
    session.flush()
    return row


def record_billing(session: Session, reconciliation: BillingReconciliation) -> BillingReconciliationRecord:
    if not reconciliation.valid():
        raise ValueError("billing_reconciliation_invalid")
    row = session.scalar(
        select(BillingReconciliationRecord).where(
            BillingReconciliationRecord.tenant_key == reconciliation.tenant_key,
            BillingReconciliationRecord.idempotency_key == reconciliation.idempotency_key,
        )
    )
    if row is None:
        row = BillingReconciliationRecord(id=str(uuid4()))
        session.add(row)
    row.tenant_key = reconciliation.tenant_key
    row.plan_state = reconciliation.plan_state
    row.quota_units = reconciliation.quota_units
    row.reserved_units = reconciliation.reserved_units
    row.usage_units = reconciliation.usage_units
    row.webhook_event_id = reconciliation.webhook_event_id
    row.webhook_status = reconciliation.webhook_status
    row.idempotency_key = reconciliation.idempotency_key
    row.failure_state = reconciliation.failure_state
    row.reconciled_at = datetime.now(timezone.utc)
    session.flush()
    return row


def freeze_candidate(session: Session, candidate: ReleaseCandidate) -> ReleaseCandidateRecord:
    row = session.scalar(
        select(ReleaseCandidateRecord).where(
            ReleaseCandidateRecord.version == candidate.version
        )
    )
    if row is None:
        row = ReleaseCandidateRecord(id=str(uuid4()))
        session.add(row)
    row.version = candidate.version
    row.commit_sha = candidate.commit_sha
    row.migration_plan_ref = candidate.migration_plan_ref
    row.environment_manifest_ref = candidate.environment_manifest_ref
    row.rollback_ref = candidate.rollback_ref
    row.evidence_ledger_ref = candidate.evidence_ledger_ref
    row.acceptance_checklist_ref = candidate.acceptance_checklist_ref
    row.frozen_at = candidate.frozen_at
    session.flush()
    return row


def record_launch_watch(session: Session, event: LaunchWatchEvent) -> LaunchWatchEventRecord:
    row = LaunchWatchEventRecord(
        id=str(uuid4()),
        candidate_version=event.candidate_version,
        event_type=event.event_type,
        severity=event.severity,
        message=event.message,
        rollback_decision=event.rollback_decision,
        occurred_at=event.occurred_at,
    )
    session.add(row)
    session.flush()
    return row
