import asyncio

import pytest
from pydantic import SecretStr


pytestmark = pytest.mark.unit


def test_webhook_setup_registers_commands(monkeypatch):
    from app.services import telegram_webhook_setup as setup

    monkeypatch.setattr(setup.settings, "telegram_enabled", True)
    monkeypatch.setattr(setup.settings, "telegram_bot_token", SecretStr("x"))
    monkeypatch.setattr(setup.settings, "telegram_gateway_secret", "s" * 40)
    monkeypatch.setattr(setup.settings, "telegram_chat_id", "-1")
    calls = []

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"ok": True}

    class Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def post(self, url, *, json):
            calls.append((url, json))
            return Response()

    monkeypatch.setattr(setup.httpx, "AsyncClient", lambda **kwargs: Client())
    asyncio.run(setup.configure_telegram_webhook())

    assert len(calls) == 2
    assert calls[0][0].endswith("/setWebhook")
    assert calls[1][0].endswith("/setMyCommands")
    assert calls[1][1]["scope"] == {"type": "chat", "chat_id": -1}
    assert {item["command"] for item in calls[1][1]["commands"]} == {
        "start", "help", "commands", "ai_status", "ai_test", "idea"
    }
