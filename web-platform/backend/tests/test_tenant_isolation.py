import pytest

from app.main import app
from app.models import Organization, OrganizationMembership, Series, User
from app.services.passwords import hash_password
from app.api.dependencies import issue_session
from app.core.config import settings
from client_utils import create_test_client
from test_foundation import TestingSession


@pytest.mark.integration
@pytest.mark.security
def test_second_tenant_cannot_read_or_mutate_first_tenant_series():
    with TestingSession() as db:
        org_a = Organization(name="Tenant A", slug="tenant-a-isolation", plan="trial")
        org_b = Organization(name="Tenant B", slug="tenant-b-isolation", plan="trial")
        db.add_all([org_a, org_b])
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

        series = Series(
            organization_id=org_a.id,
            title="Tenant A private series",
            status="draft",
        )
        db.add(series)
        db.commit()
        series_id = series.id

    second = create_test_client(app)
    try:
        token = issue_session("tenant-b-owner@narrativ.local", "owner")
        second.headers.update({"Authorization": f"Bearer {token}"})
        second.cookies.set(settings.session_cookie_name, token)
        assert second.get(f"/api/v1/series/{series_id}").status_code == 404
        assert second.patch(
            f"/api/v1/series/{series_id}",
            json={"title": "cross-tenant mutation"},
        ).status_code == 404
    finally:
        second.close()
