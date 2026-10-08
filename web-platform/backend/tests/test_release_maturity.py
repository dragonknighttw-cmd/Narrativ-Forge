from datetime import datetime, timezone

import pytest

from app.services.release_maturity import (
    BLOCKED,
    VERIFIED,
    BillingReconciliation,
    EvidenceLedgerEntry,
    ProviderAcceptance,
    ReleaseCandidate,
    validate_evidence_entry,
    launch_allowed,
)


@pytest.mark.unit
def test_verified_evidence_requires_real_references():
    now = datetime.now(timezone.utc)
    entry = EvidenceLedgerEntry(
        "worker",
        VERIFIED,
        "a" * 40,
        "run-123",
        "artifact-456",
        "release-owner",
        now,
    )
    assert validate_evidence_entry(entry) == []
    assert entry.valid()


@pytest.mark.unit
def test_verified_without_artifact_is_blocked():
    entry = EvidenceLedgerEntry("worker", VERIFIED, "a" * 40, "run-123", "", "owner", None)
    errors = validate_evidence_entry(entry)
    assert "evidence_ref_required" in errors
    assert not entry.valid()


@pytest.mark.unit
def test_waiver_requires_owner_reference():
    entry = EvidenceLedgerEntry("legal", "waived", "b" * 40, "", "", "owner", waiver_ref="")
    assert "waiver_ref_required" in validate_evidence_entry(entry)
    entry = EvidenceLedgerEntry("legal", "waived", "b" * 40, "", "", "owner", waiver_ref="approval-1")
    assert validate_evidence_entry(entry) == []


@pytest.mark.unit
def test_provider_acceptance_needs_live_acceptance():
    accepted = ProviderAcceptance("stripe", "STRIPE_SECRET_KEY", "accepted", "pass", "fallback", "accepted", "owner")
    assert accepted.ready()
    pending = ProviderAcceptance("stripe", "STRIPE_SECRET_KEY", "pending", "pending", "fallback", "pending", "owner")
    assert not pending.ready()


@pytest.mark.unit
def test_billing_reconciliation_is_idempotent_and_tracks_remaining_quota():
    record = BillingReconciliation("tenant-1", "active", 1000, 100, 250, "evt-1", "processed", "idem-1")
    assert record.valid()
    assert record.remaining_units == 650


@pytest.mark.unit
def test_launch_requires_frozen_candidate_and_evidence():
    now = datetime.now(timezone.utc)
    entry = EvidenceLedgerEntry("ci", VERIFIED, "c" * 40, "run-1", "artifact-1", "owner", now)
    candidate = ReleaseCandidate("1.2.3", "c" * 40, "mig-1", "env-1", "rollback-1", "ledger-1", "checklist-1", now)
    assert launch_allowed([entry], candidate)
    assert not launch_allowed([entry], None)
    assert not launch_allowed([EvidenceLedgerEntry("ci", BLOCKED, "c" * 40, "run-1", "artifact-1", "owner")], candidate)


def test_launch_requires_matching_evidence_commit():
    candidate = ReleaseCandidate(
        version="v1",
        commit_sha="a" * 40,
        migration_plan_ref="migration",
        environment_manifest_ref="env",
        rollback_ref="rollback",
        evidence_ledger_ref="ledger",
        acceptance_checklist_ref="acceptance",
        frozen_at=datetime.now(timezone.utc),
    )
    mismatched = EvidenceLedgerEntry(
        gate="ci",
        status=VERIFIED,
        commit_sha="b" * 40,
        workflow_run="run-1",
        evidence_ref="artifact-1",
        owner="release",
        verified_at=datetime.now(timezone.utc),
    )
    assert not launch_allowed([mismatched], candidate)
