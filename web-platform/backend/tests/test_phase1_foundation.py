from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text

from app.core.config import Settings
from app.db import Base
from app.models import core  # noqa: F401


@pytest.mark.unit
def test_production_database_url_is_supported():
    settings = Settings(
        app_env="production",
        database_url="postgresql+psycopg://user:pass@localhost/narrativ",
        session_secret="x" * 32,
        session_cookie_secure=True,
        cors_origins="https://studio.example",
        trusted_hosts="studio.example",
        storage_provider="b2",
        b2_application_key_id="id",
        b2_application_key="key",
        b2_bucket_name="bucket",
        b2_region="us-west-004",
    )
    settings.validate_runtime()
    assert settings.database_url.startswith("postgresql+psycopg://")


@pytest.mark.unit
def test_sqlite_schema_still_enforces_foreign_keys(tmp_path: Path):
    engine = create_engine(f"sqlite:///{tmp_path / 'phase1.db'}")
    Base.metadata.create_all(engine)
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar() == 0


@pytest.mark.integration
def test_postgres_schema_has_phase1_indexes(postgres_url: str):
    engine = create_engine(postgres_url)
    inspector = inspect(engine)
    assert "assets" in inspector.get_table_names()
    indexes = {item["name"] for item in inspector.get_indexes("assets")}
    assert "ix_assets_checksum_sha256" in indexes
