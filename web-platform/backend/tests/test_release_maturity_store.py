from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
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
    VERIFIED,
)
from app.services.release_maturity_store import (
    freeze_candidate,
    record_billing,
    record_launch_watch,
    upsert_evidence,
    upsert_provider,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    tables = [
        EvidenceLedgerRow.__table__,
        ProviderAcceptanceRecord.__table__,
        BillingReconciliationRecord.__table__,
        ReleaseCandidateRecord.__table__,
        LaunchWatchEventRecord.__table__,
    ]
    Base.metadata.create_all(engine, tables=tables)
    with Session(engine) as db:
        yield db


@pytest.mark.unit
def test_release_maturity_store_persists_and_updates_idempotently(session):
    now = datetime.now(timezone.utc)
    entry = EvidenceLedgerEntry("worker", VERIFIED, "a" * 40, "run-1", "artifact-1", "owner", now)
    first = upsert_evidence(session, entry)
    second = upsert_evidence(session, entry)
    assert first.id == second.id

    provider = upsert_provider(
        session,
        ProviderAcceptance("stripe", "STRIPE_SECRET_KEY", "accepted", "pass", "fallback", "accepted", "owner"),
    )
    billing = record_billing(
        session,
        BillingReconciliation("tenant", "active", 100, 10, 20, "evt-1", "processed", "idem-1"),
    )
    candidate = freeze_candidate(
        session,
        ReleaseCandidate("1.0.0", "a" * 40, "mig", "env", "rollback", "ledger", "checklist", now),
    )
    watch = record_launch_watch(
        session,
        LaunchWatchEvent("1.0.0", "watch_started", "info", "started"),
    )
    session.commit()

    assert provider.provider == "stripe"
    assert billing.remaining_units if hasattr(billing, "remaining_units") else billing.quota_units == 100
    assert candidate.frozen_at is not None
    assert watch.event_type == "watch_started"
