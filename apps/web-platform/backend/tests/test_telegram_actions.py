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
