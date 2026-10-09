import pytest
from types import SimpleNamespace
import base64

from fastapi import HTTPException

from app.main import app
from app.db import get_db
from app.models import Organization, OrganizationMembership, Series, User
from app.services.passwords import hash_password
from app.api.dependencies import get_current_membership, get_current_user
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
        membership_b = OrganizationMembership(organization_id=org_b.id, user_id=user_b.id, role="owner")
        db.add(membership_b)

        series = Series(
            organization_id=org_a.id,
            title="Tenant A private series",
            status="draft",
        )
        db.add(series)
        db.commit()
        series_id = series.id
        user_b_id = user_b.id
        user_b_email = user_b.email
        org_b_id = org_b.id

    second = create_test_client(app)
    original_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[get_current_user] = lambda: {"id": user_b_id, "email": user_b_email, "role": "owner"}
    app.dependency_overrides[get_current_membership] = lambda: SimpleNamespace(organization_id=org_b_id, user_id=user_b_id, role="owner")
    try:
        assert second.get(f"/api/v1/series/{series_id}").status_code == 404
        assert second.patch(
            f"/api/v1/series/{series_id}",
            json={"title": "cross-tenant mutation"},
        ).status_code == 404
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
        second.close()



@pytest.mark.integration
@pytest.mark.security
def test_authenticated_session_is_bound_to_selected_membership():
    from app.api.dependencies import issue_session, verify_session

    with TestingSession() as db:
        org_a = Organization(name="Tenant A", slug="tenant-a-session", plan="trial")
        org_b = Organization(name="Tenant B", slug="tenant-b-session", plan="trial")
        db.add_all([org_a, org_b])
        db.flush()

        user = User(
            email="multi-membership@narrativ.local",
            role="viewer",
            password_hash=hash_password("multi-membership-password"),
            is_active=True,
        )
        db.add(user)
        db.flush()
        db.add_all([
            OrganizationMembership(organization_id=org_a.id, user_id=user.id, role="viewer"),
            OrganizationMembership(organization_id=org_b.id, user_id=user.id, role="owner"),
        ])
        db.commit()
        user_email = user.email
        org_a_id = org_a.id
        org_b_id = org_b.id

    def override_test_db():
        with TestingSession() as session_db:
            yield session_db

    client = create_test_client(app)
    original_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = override_test_db
    try:
        session = issue_session(user_email, "owner", org_b_id)
        assert verify_session(session)["organization_id"] == org_b_id

        # Confirm the exact database dependency used by the request can see the
        # user and selected membership before asserting the HTTP behavior.
        with TestingSession() as db:
            assert db.query(User).filter(User.email == user_email, User.is_active.is_(True)).first()
            assert db.query(OrganizationMembership).filter(
                OrganizationMembership.user_id == db.query(User).filter(User.email == user_email).first().id,
                OrganizationMembership.organization_id == org_b_id,
            ).first()

        me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {session}"})
        assert me.status_code == 200, me.text
        assert me.json()["organization_id"] == org_b_id
        assert me.json()["role"] == "owner"

        switched = client.post(
            "/api/v1/auth/switch-workspace",
            json={"organization_id": org_a_id},
            headers={"Authorization": f"Bearer {session}"},
        )
        assert switched.status_code == 200, switched.text
        assert switched.json()["organization_id"] == org_a_id
        assert switched.json()["role"] == "viewer"
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
        client.close()


@pytest.mark.unit
@pytest.mark.security
def test_session_payload_versions_are_shape_checked():
    from app.api.dependencies import issue_session, verify_session

    legacy = verify_session(issue_session("legacy@narrativ.local", "viewer"))
    assert legacy["organization_id"] is None
    assert legacy["role"] == "viewer"

    workspace = verify_session(issue_session("workspace@narrativ.local", "editor", "workspace-123"))
    assert workspace["organization_id"] == "workspace-123"
    assert workspace["role"] == "editor"

    malformed_payload = "v1|workspace@narrativ.local|owner|workspace-123|9999999999|not-a-signature"
    malformed_token = base64.urlsafe_b64encode(malformed_payload.encode()).decode().rstrip("=")
    with pytest.raises(HTTPException) as error:
        verify_session(malformed_token)
    assert error.value.status_code == 401
