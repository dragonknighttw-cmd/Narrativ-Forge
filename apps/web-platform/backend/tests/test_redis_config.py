from unittest.mock import Mock

import pytest
from redis import Redis
from redis.exceptions import ConnectionError

from app.core.config import settings
from app.infrastructure.redis import create_redis_client


pytestmark = pytest.mark.unit


def test_redis_client_is_created_lazily_from_configured_url(monkeypatch):
    client = Mock(spec=Redis)
    from_url = Mock(return_value=client)
    monkeypatch.setattr(Redis, "from_url", from_url)
    monkeypatch.setattr(settings, "redis_url", "redis://localhost:6379/0")

    assert create_redis_client() is client
    from_url.assert_called_once_with("redis://localhost:6379/0", protocol=2)
    client.ping.assert_not_called()


def test_redis_client_accepts_an_explicit_url(monkeypatch):
    client = Mock(spec=Redis)
    from_url = Mock(return_value=client)
    monkeypatch.setattr(Redis, "from_url", from_url)

    assert create_redis_client("redis://localhost:6379/1") is client
    from_url.assert_called_once_with("redis://localhost:6379/1", protocol=2)


def test_redis_client_requires_configuration(monkeypatch):
    monkeypatch.setattr(settings, "redis_url", None)

    with pytest.raises(RuntimeError, match="REDIS_URL"):
        create_redis_client()


def test_redis_connection_failures_are_not_suppressed(monkeypatch):
    client = Mock(spec=Redis)
    client.ping.side_effect = ConnectionError("Redis is unavailable")
    monkeypatch.setattr(Redis, "from_url", Mock(return_value=client))

    with pytest.raises(ConnectionError, match="Redis is unavailable"):
        create_redis_client("redis://localhost:6379/0").ping()
