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


def test_google_oauth_nonce_cookie_is_short_lived_and_callback_scoped(monkeypatch):
    from starlette.responses import Response
    from app.core.config import settings

    monkeypatch.setattr(settings, "google_client_id", "test-client")
    monkeypatch.setattr(settings, "google_client_secret", "test-secret")
    monkeypatch.setattr(settings, "oauth_encryption_key", "test-oauth-state-signing-key")
    monkeypatch.setattr(settings, "session_cookie_secure", True)
    response = Response()

    google_drive.google_start(
        response,
        user={"email": "owner@example.test"},
        membership=SimpleNamespace(organization_id="org-1"),
    )

    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "secure" in cookie
    assert "samesite=lax" in cookie
    assert "max-age=600" in cookie
    assert "path=/api/v1/drive/google/callback" in cookie


def test_webhook_requires_explicit_event_subscriptions():
    with pytest.raises(ValueError):
        phase4.WebhookCreate(url="https://hooks.example.test/narrativ", events=[])
    with pytest.raises(ValueError):
        phase4.WebhookCreate(url="https://hooks.example.test/narrativ", events=["*"])
    payload = phase4.WebhookCreate(
        url="https://hooks.example.test/narrativ", events=["episode.created", "script.ready"]
    )
    assert payload.events == ["episode.created", "script.ready"]


def test_usage_record_rejects_unbounded_or_empty_fields():
    import pytest
    from pydantic import ValidationError

    for payload in (
        {"metric": "   "},
        {"metric": "render_seconds", "quantity": 100001},
        {"metric": "render_seconds", "unit": ""},
        {"metric": "render_seconds", "idempotency_key": ""},
    ):
        with pytest.raises(ValidationError):
            phase4.UsageRecord(**payload)


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


def test_telegram_api_error_logs_do_not_expose_response_body_or_bot_token(monkeypatch, caplog):
    import asyncio
    import logging
    from pydantic import SecretStr
    from app.core.config import settings
    from app.services import telegram as telegram_service

    class FakeResponse:
        status_code = 400
        text = '{"description":"invalid bot token bot-secret"}'

    class FakeClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *_args):
            return False
        async def post(self, *_args, **_kwargs):
            return FakeResponse()

    monkeypatch.setattr(settings, "telegram_bot_token", SecretStr("bot-secret"))
    monkeypatch.setattr(settings, "telegram_chat_id", "-100123")
    monkeypatch.setattr(settings, "telegram_enabled", True)
    monkeypatch.setattr(telegram_service.httpx, "AsyncClient", lambda **_kwargs: FakeClient())
    caplog.set_level(logging.WARNING)

    asyncio.run(telegram_service.send_telegram_message("safe message"))

    assert "HTTP 400" in caplog.text
    assert "bot-secret" not in caplog.text
    assert "invalid bot token" not in caplog.text


def test_telegram_domain_notification_fields_escape_html(monkeypatch):
    import asyncio
    from app.services import telegram as telegram_service
    captured = []

    async def fake_send_notification(title, details, **kwargs):
        captured.append((title, details, kwargs))

    monkeypatch.setattr(telegram_service, "send_notification", fake_send_notification)
    asyncio.run(telegram_service.notify_script_review(
        "script<id>", "Draft <script>alert(1)</script>", author="A & B"
    ))
    asyncio.run(telegram_service.notify_pipeline_error(
        "render<stage>", "provider <error> & details", project_id="project<id>"
    ))

    assert "&lt;script&gt;" in captured[0][1]
    assert "A &amp; B" in captured[0][1]
    assert "render&lt;stage&gt;" in captured[1][1]
    assert "provider &lt;error&gt; &amp; details" in captured[1][1]
    assert "project&lt;id&gt;" in captured[1][1]


def test_episode_telegram_notification_details_escape_all_dynamic_values():
    from app.api.routes.episodes import (
        _storyboard_telegram_details,
        _voiceover_telegram_details,
    )

    voiceover = _voiceover_telegram_details(
        "<script>alert(1)</script>", 123, "asset<private>"
    )
    storyboard = _storyboard_telegram_details(2, "<b>wide</b>")

    assert "<script>" not in voiceover
    assert "&lt;script&gt;" in voiceover
    assert "asset&lt;private&gt;" in voiceover
    assert "<b>wide</b>" not in storyboard
    assert "&lt;b&gt;wide&lt;/b&gt;" in storyboard


def test_ai_quota_alert_does_not_forward_raw_provider_error(monkeypatch):
    from app.services import ai_usage_tracker

    captured = []
    monkeypatch.setattr(ai_usage_tracker, "_EXHAUSTED_PROVIDERS", set())
    monkeypatch.setattr(
        ai_usage_tracker,
        "_dispatch_quota_alert",
        lambda project, provider, reason: captured.append(reason),
    )

    ai_usage_tracker.record_ai_usage(
        "openrouter",
        success=False,
        error="429 unauthorized; bearer sk-live-secret-provider-response",
    )

    assert captured == ["HTTP 429 / quota or rate limit"]
    assert "sk-live-secret" not in captured[0]



def test_cookie_session_rejects_untrusted_origin_but_bearer_auth_is_not_csrf_gated():
    from app.main import app
    from app.core.config import settings
    from client_utils import create_test_client

    client = create_test_client(app)
    client.cookies.set(settings.session_cookie_name, "invalid-session")
    rejected = client.post("/api/v1/auth/switch-workspace", json={"organization_id": "org-1"}, headers={"Origin": "https://attacker.example"})
    assert rejected.status_code == 403
    assert rejected.json()["detail"] == "Request origin is not allowed"

    client.cookies.clear()
    client.headers["Authorization"] = "Bearer invalid-session"
    bearer_request = client.post("/api/v1/auth/switch-workspace", json={"organization_id": "org-1"}, headers={"Origin": "https://attacker.example"})
    assert bearer_request.status_code == 401
