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


def test_user_listing_is_scoped_to_current_organization(db_session):
    from app.models import Organization, OrganizationMembership, User

    org_a = Organization(name="A", slug="security-a")
    org_b = Organization(name="B", slug="security-b")
    db_session.add_all([org_a, org_b])
    db_session.flush()

    user_a = User(email="a@example.com", password_hash="x", role="editor", is_active=True)
    user_b = User(email="b@example.com", password_hash="x", role="viewer", is_active=True)
    user_c = User(email="c@example.com", password_hash="x", role="owner", is_active=True)
    db_session.add_all([user_a, user_b, user_c])
    db_session.flush()
    db_session.add_all([
        OrganizationMembership(organization_id=org_a.id, user_id=user_a.id, role="owner"),
        OrganizationMembership(organization_id=org_a.id, user_id=user_b.id, role="viewer"),
        OrganizationMembership(organization_id=org_b.id, user_id=user_b.id, role="owner"),
        OrganizationMembership(organization_id=org_b.id, user_id=user_c.id, role="owner"),
    ])
    db_session.commit()

    membership = db_session.query(OrganizationMembership).filter_by(
        organization_id=org_a.id, user_id=user_a.id
    ).one()

    rows = auth.users(
        user={"id": user_a.id, "email": user_a.email, "role": "owner"},
        membership=membership,
        db=db_session,
    )
    assert {row["email"] for row in rows} == {"a@example.com", "b@example.com"}
    assert all(row["email"] != "c@example.com" for row in rows)
