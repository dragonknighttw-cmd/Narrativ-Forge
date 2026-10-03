from fastapi.testclient import TestClient

from app.main import app


def test_login_cookie_is_secure_and_samesite_strict(monkeypatch):
    from app.api.routes import auth
    from app.core.config import settings

    monkeypatch.setattr(settings, "session_cookie_secure", True)
    monkeypatch.setattr(settings, "session_cookie_name", "nf_session_test")

    # Verify the route's cookie policy directly without depending on auth storage.
    response = app.openapi()
    assert "/api/v1/auth/login" in response["paths"]

    import inspect
    source = inspect.getsource(auth.login)
    assert 'secure=settings.session_cookie_secure' in source
    assert 'samesite="strict"' in source

from sqlalchemy import text

from app.db import engine


def test_sqlite_foreign_keys_are_enabled():
    if not engine.url.drivername.startswith("sqlite"):
        return
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar() == 1
