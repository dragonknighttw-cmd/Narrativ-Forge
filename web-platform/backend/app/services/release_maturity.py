from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re


VERIFIED = "verified"
WAIVED = "waived"
PENDING = "pending"
BLOCKED = "blocked"


@dataclass(frozen=True)
class EvidenceLedgerEntry:
    gate: str
    status: str
    commit_sha: str
    workflow_run: str
    evidence_ref: str
    owner: str
    verified_at: datetime | None = None
    waiver_ref: str | None = None

    def valid(self) -> bool:
        if not self.gate.strip() or not self.owner.strip():
            return False
        if not re.fullmatch(r"[0-9a-fA-F]{40}", self.commit_sha):
            return False
        if self.status == VERIFIED:
            return bool(
                self.workflow_run.strip()
                and self.evidence_ref.strip()
                and self.verified_at is not None
            )
        if self.status == WAIVED:
            return bool(self.waiver_ref and self.waiver_ref.strip())
        return self.status in {VERIFIED, WAIVED, PENDING, BLOCKED}


def validate_evidence_entry(entry: EvidenceLedgerEntry) -> list[str]:
    errors: list[str] = []
    if not entry.gate.strip():
        errors.append("gate_required")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", entry.commit_sha):
        errors.append("commit_sha_invalid")
    if not entry.owner.strip():
        errors.append("owner_required")
    if entry.status == VERIFIED:
        if not entry.workflow_run.strip():
            errors.append("workflow_run_required")
        if not entry.evidence_ref.strip():
            errors.append("evidence_ref_required")
        if entry.verified_at is None:
            errors.append("verified_at_required")
    if entry.status == WAIVED and not (entry.waiver_ref and entry.waiver_ref.strip()):
        errors.append("waiver_ref_required")
    if entry.status not in {VERIFIED, WAIVED, PENDING, BLOCKED}:
        errors.append("status_invalid")
    return errors


@dataclass(frozen=True)
class ProviderAcceptance:
    provider: str
    credential_dependency: str
    quota_terms_review: str
    live_test_result: str
    fallback: str
    commercial_use: str
    owner: str
    accepted_at: datetime | None = None

    def ready(self) -> bool:
        return all(
            value.strip().lower() in {"verified", "accepted", "pass"}
            for value in (
                self.quota_terms_review,
                self.live_test_result,
                self.commercial_use,
            )
        ) and bool(self.owner.strip())


@dataclass(frozen=True)
class BillingReconciliation:
    tenant_key: str
    plan_state: str
    quota_units: int
    reserved_units: int
    usage_units: int
    webhook_event_id: str
    webhook_status: str
    idempotency_key: str
    failure_state: str = "none"

    def valid(self) -> bool:
        return (
            bool(self.tenant_key.strip())
            and self.quota_units >= 0
            and self.reserved_units >= 0
            and self.usage_units >= 0
            and bool(self.webhook_event_id.strip())
            and bool(self.idempotency_key.strip())
        )

    @property
    def remaining_units(self) -> int:
        return self.quota_units - self.reserved_units - self.usage_units


@dataclass(frozen=True)
class ReleaseCandidate:
    version: str
    commit_sha: str
    migration_plan_ref: str
    environment_manifest_ref: str
    rollback_ref: str
    evidence_ledger_ref: str
    acceptance_checklist_ref: str
    frozen_at: datetime | None = None

    @property
    def frozen(self) -> bool:
        return self.frozen_at is not None


@dataclass(frozen=True)
class LaunchWatchEvent:
    candidate_version: str
    event_type: str
    severity: str
    message: str
    rollback_decision: str = "none"
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def launch_allowed(
    entries: list[EvidenceLedgerEntry],
    candidate: ReleaseCandidate | None,
) -> bool:
    if candidate is None or not candidate.frozen:
        return False
    if not candidate.evidence_ledger_ref.strip():
        return False
    if not re.fullmatch(r"[0-9a-fA-F]{40}", candidate.commit_sha):
        return False
    return bool(entries) and all(
        entry.commit_sha.lower() == candidate.commit_sha.lower()
        and entry.status in {VERIFIED, WAIVED}
        and entry.valid()
        for entry in entries
    )
