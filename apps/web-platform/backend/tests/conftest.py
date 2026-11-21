import os
# Ensure safe reproducible test environment defaults
os.environ['APP_ENV'] = 'test'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['SINGLE_USER_EMAIL'] = 'test@narrativforge.local'
os.environ['STORAGE_PROVIDER'] = 'local'
os.environ['SESSION_SECRET'] = 'test-session-secret-at-least-32-chars-long'
os.environ['OAUTH_ENCRYPTION_KEY'] = 'uE8qYh4Zq9gYgJ_uYt7mY2rZq4aYv_wXy1z_2b3c4dE='
os.environ['CORS_ORIGINS'] = 'http://localhost:3000,https://narrativ-forge.vercel.app'
os.environ['SESSION_COOKIE_SECURE'] = 'false'
os.environ['STORAGE_REPLICA_ENABLED'] = 'false'
os.environ['STORAGE_REPLICA_PROVIDER'] = ''
os.environ['SUPABASE_OWNER_ORGANIZATION_SLUG'] = 'legacy-workspace'
os.environ['B2_APPLICATION_KEY_ID'] = ''
os.environ['B2_APPLICATION_KEY'] = ''

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app import models  # noqa: F401 - register all model metadata


@pytest.fixture
def db_session():
    """Provide an isolated SQLite session for unit tests that exercise DB services."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()


@pytest.fixture(autouse=True)
def preserve_global_dependency_overrides():
    from app.main import app
    from app.db import get_db
    pre_existing_get_db = app.dependency_overrides.get(get_db)
    yield
    if pre_existing_get_db is not None and get_db not in app.dependency_overrides:
        app.dependency_overrides[get_db] = pre_existing_get_db
