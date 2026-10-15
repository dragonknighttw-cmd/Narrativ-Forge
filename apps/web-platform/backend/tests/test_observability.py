import json
import logging

import pytest
import sentry_sdk
from pydantic import SecretStr

from app.core.config import settings
from app.main import app
from app.observability import (
    JsonLogFormatter,
    UvicornAccessQueryFilter,
    configure_logging,
    initialize_sentry,
)
from client_utils import create_test_client


pytestmark = pytest.mark.integration


def test_logging_configuration_selects_json_in_production_and_readable_local_format():
    configure_logging("production")
    handler = next(
        handler
        for handler in logging.getLogger().handlers
        if getattr(handler, "_narrativ_structured_handler", False)
    )
    assert isinstance(handler.formatter, JsonLogFormatter)

    configure_logging("development")
    handler = next(
        handler
        for handler in logging.getLogger().handlers
        if getattr(handler, "_narrativ_structured_handler", False)
    )
    assert not isinstance(handler.formatter, JsonLogFormatter)


def test_sentry_is_skipped_without_dsn_or_outside_deployment(monkeypatch):
    calls = []
    monkeypatch.setattr(sentry_sdk, "init", lambda **kwargs: calls.append(kwargs))

    assert initialize_sentry("", "production") is False
    assert initialize_sentry("https://public@example.invalid/1", "development") is False
    assert calls == []


def test_sentry_initialization_is_optional_and_disables_default_pii(monkeypatch):
    calls = []
    monkeypatch.setattr(sentry_sdk, "init", lambda **kwargs: calls.append(kwargs))

    initialized = initialize_sentry(
        "https://public@example.invalid/1",
        "production",
    )

    assert initialized is True
    assert calls[0]["send_default_pii"] is False
    assert calls[0]["traces_sample_rate"] == 0.0


def test_uvicorn_access_log_query_is_removed():
    record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        __file__,
        1,
        '%s - "%s %s HTTP/%s" %d',
        ("127.0.0.1", "GET", "/api/v1/health?session=secret-token", "1.1", 200),
        None,
    )

    assert UvicornAccessQueryFilter().filter(record) is True
    assert "secret-token" not in record.getMessage()
    assert "/api/v1/health" in record.getMessage()


def test_http_request_log_has_safe_context_and_omits_query_secrets(caplog, monkeypatch):
    configure_logging("production")
    monkeypatch.setattr(settings, "sentry_dsn", SecretStr("sentry-secret"))

    with caplog.at_level(logging.INFO, logger="app.http"):
        with create_test_client(app) as client:
            response = client.get("/api/v1/health?session=secret-token")

    assert response.status_code == 200
    record = next(record for record in caplog.records if record.name == "app.http")
    formatted = JsonLogFormatter().format(record)
    payload = json.loads(formatted)
    assert payload["method"] == "GET"
    assert payload["path"] == "/api/v1/health"
    assert payload["status_code"] == 200
    assert isinstance(payload["duration_ms"], (int, float))
    assert "secret-token" not in formatted
    assert "sentry-secret" not in formatted
    assert "secret-token" not in caplog.text


def test_application_imports_with_sentry_dsn_absent(monkeypatch):
    monkeypatch.setattr(settings, "sentry_dsn", SecretStr(""))

    assert app.title == "Narrativ Forge API"
    assert initialize_sentry(settings.sentry_dsn.get_secret_value(), settings.app_env) is False
