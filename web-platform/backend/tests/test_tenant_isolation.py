import pytest

from app.models import Organization, OrganizationMembership, User
from app.services.passwords import hash_password
from test_foundation import TestingSession, auth_client


@pytest.mark.integration
@pytest.mark.security
def test_second_tenant_cannot_read_or_mutate_first_tenant_series():
    first = auth_client()
    try:
        series = first.post("/api/v1/series", json={"title": "Tenant A private series"})
        assert series.status_code == 201
        series_id = series.json()["id"]

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
            db.add(OrganizationMembership(
                organization_id=org_b.id,
                user_id=user_b.id,
                role="owner",
            ))
            db.commit()

        second = first.__class__(first.app) if False else None
    finally:
        first.close()

    # Use the same application test client after seeding the second tenant.
    from client_utils import create_test_client
    second = create_test_client(first.app if hasattr(first, "app") else __import__("app.main", fromlist=["app"]).app)
    try:
        login = second.post(
            "/api/v1/auth/login",
            json={"email": "tenant-b-owner@narrativ.local", "password": "tenant-b-password-123456"},
        )
        assert login.status_code == 200
        assert second.get(f"/api/v1/series/{series_id}").status_code == 404
        assert second.patch(
            f"/api/v1/series/{series_id}",
            json={"title": "cross-tenant mutation"},
        ).status_code in {403, 404, 405}
    finally:
        second.close()
