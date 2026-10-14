import pytest

from app.api.dependencies import get_current_membership, get_current_user
from app.db import get_db
from app.main import app
from app.models import Organization, OrganizationMembership, Series, User
from client_utils import create_test_client


@pytest.mark.integration
@pytest.mark.security
def test_series_bible_persists_characters_and_enforces_tenant_scope(db_session):
    org_a = Organization(name="Bible Tenant A", slug="bible-tenant-a")
    org_b = Organization(name="Bible Tenant B", slug="bible-tenant-b")
    user_a = User(email="bible-a@test.local", role="owner", password_hash="dummy")
    user_b = User(email="bible-b@test.local", role="owner", password_hash="dummy")
    db_session.add_all([org_a, org_b, user_a, user_b])
    db_session.flush()

    membership_a = OrganizationMembership(organization_id=org_a.id, user_id=user_a.id, role="owner")
    membership_b = OrganizationMembership(organization_id=org_b.id, user_id=user_b.id, role="owner")
    series = Series(organization_id=org_a.id, title="Persistent Series Bible")
    db_session.add_all([membership_a, membership_b, series])
    db_session.commit()

    original_overrides = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: {
        "id": user_a.id,
        "email": user_a.email,
        "role": "owner",
        "organization_id": org_a.id,
    }
    app.dependency_overrides[get_current_membership] = lambda: membership_a
    client = create_test_client(app)

    character = {
        "id": "character-zeyar",
        "name": "ဇေယျာ",
        "role": "protagonist",
        "tone": "Curious and energetic",
        "catchphrase": "သင်ရော ဒါကို သတိထားမိဖူးလား?",
        "traits": "Yangon-based investigator",
    }
    try:
        initial = client.get(f"/api/v1/series/{series.id}/bible")
        assert initial.status_code == 200
        assert initial.json()["characters"] == []

        saved = client.put(
            f"/api/v1/series/{series.id}/bible",
            json={"characters": [character]},
        )
        assert saved.status_code == 200, saved.text
        assert saved.json()["characters"] == [character]

        # Read back from the API to prove the data is persisted, not only held in UI state.
        reread = client.get(f"/api/v1/series/{series.id}/bible")
        assert reread.status_code == 200
        assert reread.json()["characters"] == [character]

        app.dependency_overrides[get_current_user] = lambda: {
            "id": "viewer-user",
            "email": "viewer@test.local",
            "role": "viewer",
            "organization_id": org_a.id,
        }
        assert client.put(
            f"/api/v1/series/{series.id}/bible",
            json={"characters": []},
        ).status_code == 403

        app.dependency_overrides[get_current_user] = lambda: {
            "id": user_b.id,
            "email": user_b.email,
            "role": "owner",
            "organization_id": org_b.id,
        }
        app.dependency_overrides[get_current_membership] = lambda: membership_b
        assert client.get(f"/api/v1/series/{series.id}/bible").status_code == 404
        assert client.put(
            f"/api/v1/series/{series.id}/bible",
            json={"characters": []},
        ).status_code == 404
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
        client.close()
