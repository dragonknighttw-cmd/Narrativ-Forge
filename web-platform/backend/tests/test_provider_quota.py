import pytest

pytestmark = pytest.mark.unit

from datetime import datetime, timezone

import pytest

from app.services.provider_quota import (
    ProviderQuotaExceeded,
    get_provider_quota,
    reserve_provider_quota,
)


def test_provider_quota_reservation_and_idempotency(db_session):
    db = db_session
    from app.models import Organization

    org = Organization(name="quota", slug="quota-test")
    db.add(org)
    db.commit()

    now = datetime(2026, 10, 7, 12, tzinfo=timezone.utc)
    first = reserve_provider_quota(
        db,
        org.id,
        "groq",
        100,
        idempotency_key="groq:test:1",
        now=now,
    )
    db.commit()
    assert first.used == 100
    assert first.remaining == 900

    second = reserve_provider_quota(
        db,
        org.id,
        "groq",
        100,
        idempotency_key="groq:test:1",
        now=now,
    )
    assert second.used == 100

    db.close()


def test_provider_quota_rejects_over_budget(db_session, monkeypatch):
    db = db_session
    from app.models import Organization

    org = Organization(name="quota2", slug="quota-test-2")
    db.add(org)
    db.commit()

    with pytest.raises(ProviderQuotaExceeded):
        reserve_provider_quota(
            db,
            org.id,
            "agnes",
            501,
            idempotency_key="agnes:test:1",
            now=datetime(2026, 10, 7, tzinfo=timezone.utc),
        )

    db.rollback()
    quota = get_provider_quota(db, org.id, "agnes")
    assert quota.used == 0
    assert quota.remaining == 500
    db.close()


def test_provider_quota_reused_key_cannot_change_provider(db_session):
    db = db_session
    from app.models import Organization

    org = Organization(name="quota3", slug="quota-test-3")
    db.add(org)
    db.commit()
    now = datetime(2026, 10, 7, 12, tzinfo=timezone.utc)

    reserve_provider_quota(
        db, org.id, "groq", 10, idempotency_key="shared-key", now=now
    )
    db.commit()

    with pytest.raises(ValueError, match="different provider quota reservation"):
        reserve_provider_quota(
            db, org.id, "agnes", 1, idempotency_key="shared-key", now=now
        )


def test_provider_quota_exposes_warning_and_fallback_thresholds(db_session, monkeypatch):
    db = db_session
    from app.models import Organization

    monkeypatch.setattr("app.services.provider_quota.settings.groq_daily_requests_budget", 100)
    monkeypatch.setattr("app.services.provider_quota.settings.provider_quota_warning_threshold", 0.80)
    monkeypatch.setattr("app.services.provider_quota.settings.provider_quota_fallback_threshold", 0.95)

    org = Organization(name="quota4", slug="quota-test-4")
    db.add(org)
    db.commit()
    now = datetime(2026, 10, 7, 12, tzinfo=timezone.utc)

    reserve_provider_quota(
        db, org.id, "groq", 95, idempotency_key="threshold-key", now=now
    )
    db.commit()
    quota = get_provider_quota(db, org.id, "groq", now=now)
    assert quota.warning is True
    assert quota.fallback is True
    assert quota.remaining == 5
