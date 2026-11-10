import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import Response

from app.api.routes import google_drive, phase4
from app.api.routes.phase4 import UsageRecord, WebhookCreate
from client_utils import create_test_client
from app.main import app


pytestmark = pytest.mark.security


def test_google_oauth_state_contains_signed_random_nonce(monkeypatch):
    monkeypatch.setattr(google_drive.settings, "oauth_encryption_key", "test-oauth-encryption-key")
    state_a = google_drive._state("owner@example.test", "org-a", "a" * 43)
    state_b = google_drive._state("owner@example.test", "org-a", "b" * 43)

    assert state_a != state_b
    assert google_drive._verify_state(state_a) == ("owner@example.test", "org-a", "a" * 43)


def test_google_oauth_callback_rejects_state_without_matching_browser_cookie(monkeypatch):
    monkeypatch.setattr(google_drive.settings, "oauth_encryption_key", "test-oauth-encryption-key")
    state = google_drive._state("owner@example.test", "org-a", "a" * 43)
    request = Request({"type": "http", "method": "GET", "path": "/", "headers": [], "query_string": b""})

    with pytest.raises(HTTPException) as raised:
        asyncio.run(google_drive.google_callback("oauth-code", state, request, Response(), db=MagicMock()))

    assert raised.value.status_code == 400
    assert "browser session" in raised.value.detail


def test_webhook_requires_explicit_event_subscriptions():
    with pytest.raises(ValidationError):
        WebhookCreate(url="https://hooks.example.test/narrativ", events=[])

    payload = WebhookCreate(
        url="https://hooks.example.test/narrativ",
        events=["episode.created", "script.approved", "episode.created"],
    )
    assert payload.events == ["episode.created", "script.approved"]


def test_paid_plan_cannot_be_set_by_api_owner():
    with pytest.raises(HTTPException) as raised:
        phase4.set_plan(
            "business",
            membership=SimpleNamespace(organization_id="org-a"),
            user={"role": "owner"},
            db=MagicMock(),
        )

    assert raised.value.status_code == 410


def test_usage_idempotency_key_is_scoped_to_workspace():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    membership = SimpleNamespace(organization_id="org-a")

    phase4.record_usage(
        UsageRecord(metric="render_seconds", quantity=30, idempotency_key="same-key"),
        membership=membership,
        db=db,
    )

    event = db.add.call_args.args[0]
    assert event.organization_id == "org-a"
    assert event.idempotency_key == "org-a:same-key"


@pytest.mark.integration
def test_ai_usage_endpoint_requires_authentication():
    response = create_test_client(app).get("/api/v1/ai/usage")
    assert response.status_code == 401

def test_telegram_api_error_logs_do_not_expose_response_body_or_bot_token(monkeypatch, caplog):
    import logging
    from app.services import telegram as telegram_service
    from app.core.config import settings
    from pydantic import SecretStr

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


def test_telegram_domain_notifications_escape_dynamic_html(monkeypatch):
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


@pytest.mark.parametrize("payload", [
    {"metric": "   "},
    {"metric": "render_seconds", "quantity": 100001},
    {"metric": "render_seconds", "unit": ""},
])
def test_usage_record_rejects_unbounded_or_empty_fields(payload):
    with pytest.raises(ValidationError):
        UsageRecord(**payload)


def test_google_oauth_start_sets_short_lived_httponly_state_cookie(monkeypatch):
    from urllib.parse import parse_qs, urlparse

    monkeypatch.setattr(google_drive.settings, "google_client_id", "google-client")
    monkeypatch.setattr(google_drive.settings, "google_client_secret", "google-secret")
    monkeypatch.setattr(google_drive.settings, "oauth_encryption_key", "test-oauth-encryption-key")
    monkeypatch.setattr(google_drive.settings, "session_cookie_secure", True)
    response = Response()

    result = google_drive.google_start(
        response,
        user={"email": "owner@example.test"},
        membership=SimpleNamespace(organization_id="org-a"),
    )

    state = parse_qs(urlparse(result["authorization_url"]).query)["state"][0]
    assert google_drive._verify_state(state)[0:2] == ("owner@example.test", "org-a")
    cookie = response.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "secure" in cookie
    assert "samesite=lax" in cookie
    assert "max-age=600" in cookie
    assert "path=/api/v1/drive/google/callback" in cookie
