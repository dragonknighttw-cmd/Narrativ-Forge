import pytest
from alembic.config import Config
from sqlalchemy import event

from app.core.config import Settings
from app.db import _set_sqlite_foreign_keys, create_database_engine


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
