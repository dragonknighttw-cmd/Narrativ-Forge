import pytest
from fastapi import HTTPException


pytestmark = pytest.mark.unit


def test_telegram_gateway_rejects_when_not_configured(monkeypatch):
    from app.api.routes import telegram

    monkeypatch.setattr(telegram.settings, "telegram_gateway_secret", "")
    monkeypatch.setattr(telegram.settings, "telegram_allowed_user_ids", "")
    with pytest.raises(HTTPException) as exc:
        telegram._authorize_gateway("any-value", 12345)
    assert exc.value.status_code == 503


def test_telegram_gateway_rejects_wrong_secret(monkeypatch):
    from app.api.routes import telegram

    monkeypatch.setattr(telegram.settings, "telegram_gateway_secret", "s" * 40)
    monkeypatch.setattr(telegram.settings, "telegram_allowed_user_ids", "12345")
    with pytest.raises(HTTPException) as exc:
        telegram._authorize_gateway("wrong-secret", 12345)
    assert exc.value.status_code == 401


def test_telegram_gateway_rejects_unapproved_user(monkeypatch):
    from app.api.routes import telegram

    monkeypatch.setattr(telegram.settings, "telegram_gateway_secret", "s" * 40)
    monkeypatch.setattr(telegram.settings, "telegram_allowed_user_ids", "12345,67890")
    with pytest.raises(HTTPException) as exc:
        telegram._authorize_gateway("s" * 40, 55555)
    assert exc.value.status_code == 403


def test_telegram_gateway_accepts_secret_and_allowlisted_user(monkeypatch):
    from app.api.routes import telegram

    monkeypatch.setattr(telegram.settings, "telegram_gateway_secret", "s" * 40)
    monkeypatch.setattr(telegram.settings, "telegram_allowed_user_ids", "12345,67890")
    assert telegram._authorize_gateway("s" * 40, 12345) is None


def test_telegram_event_id_is_stable_for_retries():
    from app.api.routes.telegram import _event_pk

    assert _event_pk("callback-query-123") == _event_pk("callback-query-123")
    assert _event_pk("callback-query-123") != _event_pk("callback-query-124")


def test_script_approval_persists_and_duplicate_event_is_idempotent(db_session, monkeypatch):
    import asyncio

    from app.models import Episode, Organization, Script, Series
    from app.api.routes import telegram

    monkeypatch.setattr(telegram.settings, "telegram_gateway_secret", "s" * 40)
    monkeypatch.setattr(telegram.settings, "telegram_allowed_user_ids", "12345")
    monkeypatch.setattr(telegram.settings, "telegram_chat_id", "-100123")
    monkeypatch.setattr(telegram.settings, "telegram_topic_id", 6)

    async def no_message(*_args, **_kwargs):
        return None

    monkeypatch.setattr(telegram, "send_telegram_message", no_message)

    organization = Organization(name="Test Org", slug="legacy-workspace")
    db_session.add(organization)
    db_session.flush()
    series = Series(organization_id=organization.id, title="Test Series")
    db_session.add(series)
    db_session.flush()
    episode = Episode(
        organization_id=organization.id,
        public_id="telegram-test-episode",
        series_id=series.id,
        episode_number=1,
        title="Telegram Test Episode",
    )
    db_session.add(episode)
    db_session.flush()
    script = Script(
        episode_id=episode.id,
        version=1,
        title="Test Script",
        content="A test script",
        status="draft",
        is_current=True,
    )
    db_session.add(script)
    db_session.commit()

    payload = telegram.TelegramActionPayload(
        action=f"nf_script_appr:{script.id}",
        event_id="telegram-callback-script-approval-1",
        user_id=12345,
        username="approved-user",
        chat_id="-100123",
        topic_id=6,
    )
    result = asyncio.run(
        telegram.handle_telegram_action(
            payload,
            x_telegram_gateway_secret="s" * 40,
            db=db_session,
        )
    )
    assert result["status"] == "ok"
    assert db_session.get(Script, script.id).status == "approved"

    duplicate = asyncio.run(
        telegram.handle_telegram_action(
            payload,
            x_telegram_gateway_secret="s" * 40,
            db=db_session,
        )
    )
    assert duplicate["status"] == "duplicate"
    assert duplicate["id"] == script.id



def test_telegram_webhook_rejects_missing_or_wrong_secret(monkeypatch):
    import asyncio
    from app.api.routes import telegram

    monkeypatch.setattr(telegram.settings, "telegram_gateway_secret", "s" * 40)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(telegram.telegram_webhook(
            {"callback_query": {}},
            x_telegram_bot_api_secret_token="wrong",
            db=None,
        ))
    assert exc.value.status_code == 401


def test_telegram_webhook_ignores_non_callback_updates(monkeypatch):
    import asyncio
    from app.api.routes import telegram

    monkeypatch.setattr(telegram.settings, "telegram_gateway_secret", "s" * 40)
    assert asyncio.run(telegram.telegram_webhook(
        {"update_id": 123, "message": {"text": "hello"}},
        x_telegram_bot_api_secret_token="s" * 40,
        db=None,
    )) == {"status": "ignored"}


def test_telegram_webhook_dispatches_callback_to_action_handler(monkeypatch):
    import asyncio
    from app.api.routes import telegram

    monkeypatch.setattr(telegram.settings, "telegram_gateway_secret", "s" * 40)
    monkeypatch.setattr(telegram.settings, "telegram_chat_id", "-100123")
    monkeypatch.setattr(telegram.settings, "telegram_topic_id", 6)
    calls = {}

    async def fake_action(payload, *, x_telegram_gateway_secret, db):
        calls["payload"] = payload
        calls["secret"] = x_telegram_gateway_secret
        return {"status": "ok", "action": "telegram.script.approved", "id": "script-1"}

    async def fake_answer(*args, **kwargs):
        calls["answered"] = (args, kwargs)

    monkeypatch.setattr(telegram, "handle_telegram_action", fake_action)
    monkeypatch.setattr(telegram, "answer_telegram_callback", fake_answer)
    result = asyncio.run(telegram.telegram_webhook(
        {
            "update_id": 1,
            "callback_query": {
                "id": "callback-1",
                "from": {"id": 12345, "username": "reviewer"},
                "data": "nf_script_appr:script-1",
                "message": {
                    "message_thread_id": 88,
                    "chat": {"id": -100123},
                    "text": "Review script",
                },
            },
        },
        x_telegram_bot_api_secret_token="s" * 40,
        db=object(),
    ))
    assert result["status"] == "ok"
    assert calls["payload"].event_id == "callback-1"
    assert calls["payload"].user_id == 12345
    assert calls["payload"].topic_id == 88
    assert calls["payload"].action == "nf_script_appr:script-1"
    assert calls["secret"] == "s" * 40
    assert "answered" in calls



@pytest.mark.parametrize(
    ("topic_id", "project_name"),
    [(6, "Narrativ Forge"), (2, "A Little World With Us"), (5, "Logixa Flow"), (18, "Doka"), (7, "Cognix")],
)
def test_telegram_commands_are_scoped_to_project_topic(monkeypatch, topic_id, project_name):
    import asyncio
    from app.api.routes import telegram

    monkeypatch.setattr(telegram.settings, "telegram_gateway_secret", "s" * 40)
    monkeypatch.setattr(telegram.settings, "telegram_allowed_user_ids", "12345")
    monkeypatch.setattr(telegram.settings, "telegram_chat_id", "-100123")
    monkeypatch.setattr(telegram.settings, "telegram_topic_id", 6)
    sent = []

    async def fake_send(text, **kwargs):
        sent.append((text, kwargs))
        return {"ok": True}

    monkeypatch.setattr(telegram, "send_telegram_message", fake_send)
    for command in ("/start", "/ai_status"):
        result = asyncio.run(telegram.telegram_webhook(
            {
                "update_id": topic_id,
                "message": {
                    "text": command,
                    "from": {"id": 12345},
                    "chat": {"id": -100123, "type": "supergroup"},
                    "message_thread_id": topic_id,
                },
            },
            x_telegram_bot_api_secret_token="s" * 40,
            db=None,
        ))
        assert result["project"] == project_name
        assert sent[-1][1]["topic_id"] == topic_id
        assert project_name in sent[-1][0]
        if topic_id != 6 and command == "/ai_status":
            assert "not connected to this Narrativ Forge backend" in sent[-1][0]
            assert "Narrativ Forge status" not in sent[-1][0]
