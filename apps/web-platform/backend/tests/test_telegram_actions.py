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
