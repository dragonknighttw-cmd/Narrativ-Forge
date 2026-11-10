from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.routes import google_drive, phase4
from app.models import UsageEvent

pytestmark = pytest.mark.unit


def test_google_oauth_state_is_signed_and_contains_browser_nonce(monkeypatch):
    monkeypatch.setattr(google_drive.settings, "oauth_encryption_key", "test-oauth-state-signing-key")
    state, nonce = google_drive._state("owner@example.test", "org-1")
    email, organization_id, verified_nonce = google_drive._verify_state(state)
    assert (email, organization_id, verified_nonce) == ("owner@example.test", "org-1", nonce)
    with pytest.raises(HTTPException) as raised:
        google_drive._verify_state(state[:-4] + "xxxx")
    assert raised.value.status_code == 400


def test_webhook_requires_explicit_event_subscriptions():
    with pytest.raises(ValueError):
        phase4.WebhookCreate(url="https://hooks.example.test/narrativ", events=[])
    with pytest.raises(ValueError):
        phase4.WebhookCreate(url="https://hooks.example.test/narrativ", events=["*"])
    payload = phase4.WebhookCreate(
        url="https://hooks.example.test/narrativ", events=["episode.created", "script.ready"]
    )
    assert payload.events == ["episode.created", "script.ready"]


def test_manual_billing_plan_change_is_disabled():
    with pytest.raises(HTTPException) as raised:
        phase4.set_plan("business", membership=SimpleNamespace(organization_id="org-1"), user={"role": "owner"}, db=object())
    assert raised.value.status_code == 410


def test_usage_idempotency_constraint_is_tenant_scoped():
    constraints = [
        item for item in UsageEvent.__table__.constraints
        if getattr(item, "name", None) == "uq_usage_event_org_idempotency"
    ]
    assert len(constraints) == 1
    assert [column.name for column in constraints[0].columns] == ["organization_id", "idempotency_key"]


def test_telegram_notification_escapes_dynamic_html(monkeypatch):
    import asyncio
    from app.services import telegram

    captured = {}

    async def fake_send(text, **kwargs):
        captured["text"] = text
        return {"ok": True}

    monkeypatch.setattr(telegram, "send_telegram_message", fake_send)
    asyncio.run(telegram.send_notification("<b>unsafe title</b>", "<i>trusted markup</i>"))

    assert "&lt;b&gt;unsafe title&lt;/b&gt;" in captured["text"]
    assert "<i>trusted markup</i>" in captured["text"]


def test_whisper_usage_claims_include_workspace_binding(monkeypatch):
    import time
    from app.api.routes.cloud_processing import _sign, _verify_signed_payload
    from app.core.config import settings

    monkeypatch.setattr(settings, "cloudflare_whisper_shared_secret", "test-secret")
    token = _sign({
        "purpose": "usage",
        "sub": "user-1",
        "organization_id": "org-1",
        "episode_id": "episode-1",
        "exp": int(time.time()) + 60,
        "jti": "usage-org-1",
        "max_audio_seconds": 120,
    })
    claims = _verify_signed_payload(token)
    assert claims["organization_id"] == "org-1"
    assert claims["episode_id"] == "episode-1"
