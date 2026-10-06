from datetime import datetime, timezone

import pytest

from app.services.provider_quota import (
    ProviderQuotaExceeded,
    get_provider_quota,
    reserve_provider_quota,
)


def test_provider_quota_reservation_and_idempotency(testing_db):
    db = testing_db()
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


def test_provider_quota_rejects_over_budget(testing_db, monkeypatch):
    db = testing_db()
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
