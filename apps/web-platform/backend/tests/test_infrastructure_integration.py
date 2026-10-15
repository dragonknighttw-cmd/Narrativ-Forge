import pytest
from sqlalchemy import text

from app.core.config import settings
from app.db import engine
from app.infrastructure.redis import create_redis_client


pytestmark = pytest.mark.integration


def test_postgresql_service_is_reachable_and_migrated():
    if engine.dialect.name != "postgresql":
        pytest.skip("DATABASE_URL is not configured for PostgreSQL integration")

    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
        assert connection.execute(text("SELECT version_num FROM alembic_version")).first()


def test_redis_service_is_reachable():
    if not settings.redis_url:
        pytest.skip("REDIS_URL is not configured for Redis integration")

    client = create_redis_client()
    try:
        assert client.ping() is True
    finally:
        client.close()
