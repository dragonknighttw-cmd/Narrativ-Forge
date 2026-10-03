from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.routes import auth
from app.core.config import settings
from app.db import engine, get_db
from app.main import app


def test_login_cookie_is_secure_and_samesite_strict(monkeypatch):
    class FakeQuery:
        def filter(self, *_args):
            return self

        def first(self):
            return type(
                "UserStub",
                (),
                {"email": "admin@narrativ.local", "role": "owner", "id": 1, "password_hash": "unused"},
            )()

    class FakeDB:
        def query(self, *_args):
            return FakeQuery()

    monkeypatch.setattr(settings, "session_cookie_secure", True)
    monkeypatch.setattr(settings, "session_cookie_name", "nf_session_test")
    monkeypatch.setattr(auth, "issue_session", lambda email, role: "signed-test-session")
    monkeypatch.setattr(auth, "verify_password", lambda password, password_hash: True)

    app.dependency_overrides[get_db] = lambda: FakeDB()
    try:
        response = TestClient(app).post(
            "/api/v1/auth/login",
            json={"email": "admin@narrativ.local", "password": "test-password"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    cookie = response.headers["set-cookie"]
    assert "Secure" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=Strict" in cookie


def test_sqlite_foreign_keys_are_enabled():
    if not engine.url.drivername.startswith("sqlite"):
        return
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar() == 1
