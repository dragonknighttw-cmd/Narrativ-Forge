import pytest
from alembic.config import Config
from sqlalchemy import event

from app.core.config import Settings
from app.db import _set_sqlite_foreign_keys, create_database_engine, normalize_database_url


pytestmark = pytest.mark.unit


def test_sqlite_database_url_keeps_sqlite_connection_behavior():
    settings = Settings(database_url="sqlite:///:memory:")
    engine = create_database_engine(settings.database_url)
    try:
        assert engine.dialect.name == "sqlite"
        assert event.contains(engine, "connect", _set_sqlite_foreign_keys)
        with engine.connect() as connection:
            assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
    finally:
        engine.dispose()


def test_postgresql_url_is_accepted_without_sqlite_connection_behavior():
    settings = Settings(database_url="postgresql://user@localhost/narrativ")
    engine = create_database_engine(settings.database_url)
    try:
        assert str(engine.url) == settings.database_url
        assert engine.dialect.name == "postgresql"
        assert not event.contains(engine, "connect", _set_sqlite_foreign_keys)
    finally:
        engine.dispose()


def test_alembic_config_preserves_encoded_database_url():
    database_url = "postgresql://user:p%40ss%25word@localhost/narrativ"
    config = Config()

    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

    assert config.get_main_option("sqlalchemy.url") == database_url


def test_postgresql_url_preserves_url_encoded_credentials():
    database_url = "postgresql://test-user:test%40pass%3Aword%2Fpart%25tag%23hash@localhost/narrativ"
    engine = create_database_engine(database_url)
    try:
        assert engine.dialect.name == "postgresql"
        assert engine.url.password == "test@pass:word/part%tag#hash"
        assert engine.url.render_as_string(hide_password=False) == database_url
    finally:
        engine.dispose()


def test_legacy_postgres_url_is_normalized_without_losing_credentials():
    database_url = "postgres://test-user:test%40pass%3Aword@localhost/narrativ"

    normalized_url = normalize_database_url(database_url)

    assert normalized_url.drivername == "postgresql"
    assert normalized_url.password == "test@pass:word"
