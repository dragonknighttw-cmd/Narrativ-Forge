import pytest

from app.api.routes import auth
from app.core.config import settings
from app.db import get_db
from app.main import app
from client_utils import create_test_client


pytestmark = pytest.mark.security


@pytest.mark.integration
def test_security_headers_are_present():
    response = create_test_client(app).get("/")
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "same-origin"


@pytest.mark.integration
def test_login_rate_limit_counts_failed_attempts_only(monkeypatch):
    class FakeQuery:
        def filter(self, *_args):
            return self
        def first(self):
            return None

    class FakeDB:
        def query(self, *_args):
            return FakeQuery()

    app.dependency_overrides[get_db] = lambda: FakeDB()
    monkeypatch.setattr(settings, "single_user_mode", False)
    try:
        from app import main
        main._rate_windows.clear()
        client = create_test_client(app)
        responses = [
            client.post("/api/v1/auth/login", json={"email": "unknown@example.com", "password": "bad"})
            for _ in range(31)
        ]
        assert responses[-1].status_code == 429
    finally:
        app.dependency_overrides.pop(get_db, None)
