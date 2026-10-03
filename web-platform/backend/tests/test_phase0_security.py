import pytest
from pydantic import ValidationError
from sqlalchemy import text

from app.api.routes import auth
from app.api.routes.auth import LoginRequest
from app.core.config import settings
from app.db import engine, get_db
from app.main import app
from client_utils import create_test_client


def test_login_email_validation_accepts_project_local_address():
    payload = LoginRequest(email="ADMIN@narrativ.local", password="test-password")

    assert payload.email == "admin@narrativ.local"


@pytest.mark.parametrize("email", ["adminnarrativ.local", "admin@ narrativ.local", "admin@narrativ"])
def test_login_email_validation_rejects_malformed_address(email):
    with pytest.raises(ValidationError):
        LoginRequest(email=email, password="test-password")


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
        response = create_test_client(app).post(
            "/api/v1/auth/login",
            json={"email": "admin@narrativ.local", "password": "test-password"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    cookie = response.headers["set-cookie"]
    assert "Secure" in cookie
    assert "HttpOnly" in cookie
    assert "samesite=strict" in cookie.lower()


def test_sqlite_foreign_keys_are_enabled():
    if not engine.url.drivername.startswith("sqlite"):
        return
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA foreign_keys")).scalar() == 1
