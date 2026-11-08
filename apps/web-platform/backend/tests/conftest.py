import os
# Ensure safe reproducible test environment defaults
os.environ.setdefault('APP_ENV', 'test')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('SINGLE_USER_EMAIL', 'test@narrativforge.local')
os.environ.setdefault('STORAGE_PROVIDER', 'local')
os.environ.setdefault('SESSION_SECRET', 'test-session-secret-at-least-32-chars-long')
os.environ.setdefault('OAUTH_ENCRYPTION_KEY', 'uE8qYh4Zq9gYgJ_uYt7mY2rZq4aYv_wXy1z_2b3c4dE=')

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
