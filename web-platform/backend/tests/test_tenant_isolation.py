import pytest

from app.main import app
from app.models import Organization, OrganizationMembership, User
from app.services.passwords import hash_password
from app.api.dependencies import issue_session
from app.core.config import settings
from client_utils import create_test_client
from test_foundation import TestingSession, auth_client


@pytest.mark.integration
@pytest.mark.security
def test_second_tenant_cannot_read_or_mutate_first_tenant_series():
    first = auth_client()
    try:
        series = first.post("/api/v1/series", json={"title": "Tenant A private series"})
        assert series.status_code == 201
        series_id = series.json()["id"]
    finally:
        first.close()

    with TestingSession() as db:
        org_b = Organization(name="Tenant B", slug="tenant-b-isolation", plan="trial")
        db.add(org_b)
        db.flush()
        user_b = User(
            email="tenant-b-owner@narrativ.local",
            role="owner",
            password_hash=hash_password("tenant-b-password-123456"),
            is_active=True,
        )
        db.add(user_b)
        db.flush()
        db.add(OrganizationMembership(organization_id=org_b.id, user_id=user_b.id, role="owner"))
        db.commit()

    second = create_test_client(app)
    try:
        second.cookies.set(
            settings.session_cookie_name,
            issue_session("tenant-b-owner@narrativ.local", "owner"),
        )
        assert second.get(f"/api/v1/series/{series_id}").status_code == 404
        assert second.patch(
            f"/api/v1/series/{series_id}",
            json={"title": "cross-tenant mutation"},
        ).status_code == 404
    finally:
        second.close()
