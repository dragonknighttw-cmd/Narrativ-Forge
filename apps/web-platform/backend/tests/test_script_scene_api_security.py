import pytest

from app.api.dependencies import get_current_membership, get_current_user
from app.db import get_db
from app.main import app
from app.models import (
    Episode,
    Organization,
    OrganizationMembership,
    Series,
    User,
)
from client_utils import create_test_client


@pytest.mark.integration
@pytest.mark.security
def test_script_and_scene_api_versioning_and_tenant_guards(db_session):
    org_a = Organization(name="Studio Tenant A", slug="studio-tenant-a")
    org_b = Organization(name="Studio Tenant B", slug="studio-tenant-b")
    owner_a = User(email="studio-owner-a@test.local", role="owner", password_hash="dummy")
    viewer_a = User(email="studio-viewer-a@test.local", role="viewer", password_hash="dummy")
    owner_b = User(email="studio-owner-b@test.local", role="owner", password_hash="dummy")
    db_session.add_all([org_a, org_b, owner_a, viewer_a, owner_b])
    db_session.flush()

    member_owner_a = OrganizationMembership(
        organization_id=org_a.id, user_id=owner_a.id, role="owner"
    )
    member_viewer_a = OrganizationMembership(
        organization_id=org_a.id, user_id=viewer_a.id, role="viewer"
    )
    member_owner_b = OrganizationMembership(
        organization_id=org_b.id, user_id=owner_b.id, role="owner"
    )
    series_a = Series(organization_id=org_a.id, title="Studio Series A")
    series_b = Series(organization_id=org_b.id, title="Studio Series B")
    db_session.add_all(
        [member_owner_a, member_viewer_a, member_owner_b, series_a, series_b]
    )
    db_session.flush()

    episode_a = Episode(
        organization_id=org_a.id,
        series_id=series_a.id,
        public_id="studio_tenant_a_001",
        episode_number=1,
        title="Studio Episode A",
        status="script_review",
    )
    episode_b = Episode(
        organization_id=org_b.id,
        series_id=series_b.id,
        public_id="studio_tenant_b_001",
        episode_number=1,
        title="Studio Episode B",
        status="script_review",
    )
    db_session.add_all([episode_a, episode_b])
    db_session.commit()

    original_overrides = dict(app.dependency_overrides)
    active_user = {
        "id": owner_a.id,
        "email": owner_a.email,
        "role": "owner",
        "organization_id": org_a.id,
    }
    active_membership = member_owner_a
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: active_user
    app.dependency_overrides[get_current_membership] = lambda: active_membership
    client = create_test_client(app)

    try:
        created = client.post(
            f"/api/v1/episodes/{episode_a.id}/scripts",
            json={"title": "ပထမမူကြမ်း", "content": "ဇာတ်ညွှန်းအကြောင်းအရာ"},
        )
        assert created.status_code == 201, created.text
        first = created.json()
        assert first["version"] == 1
        assert first["is_current"] is True
        assert first["row_version"] == 1

        updated = client.patch(
            f"/api/v1/scripts/{first['id']}",
            json={
                "title": "ပြင်ဆင်ထားသော မူကြမ်း",
                "content": "ပြင်ဆင်ထားသော ဇာတ်ညွှန်း",
                "expected_row_version": 1,
            },
        )
        assert updated.status_code == 200, updated.text
        assert updated.json()["row_version"] == 2

        stale = client.patch(
            f"/api/v1/scripts/{first['id']}",
            json={"content": "stale overwrite", "expected_row_version": 1},
        )
        assert stale.status_code == 409
        assert stale.json()["detail"]["code"] == "STALE_ROW_VERSION"

        versioned = client.post(
            f"/api/v1/episodes/{episode_a.id}/scripts/versions",
            json={"title": "ဒုတိယမူကြမ်း", "content": "ဒုတိယမူကြမ်းအကြောင်းအရာ"},
        )
        assert versioned.status_code == 201, versioned.text
        current_script = versioned.json()
        assert current_script["version"] == 2
        assert current_script["is_current"] is True

        historical_edit = client.patch(
            f"/api/v1/scripts/{first['id']}",
            json={"content": "historical overwrite", "expected_row_version": 2},
        )
        assert historical_edit.status_code == 409
        assert historical_edit.json()["detail"]["code"] == "HISTORICAL_SCRIPT_IMMUTABLE"

        # Scene endpoints must not attach another episode's script to this episode.
        other_script = client.post(
            f"/api/v1/episodes/{episode_b.id}/scripts",
            json={"title": "Other tenant script", "content": "private"},
        )
        assert other_script.status_code == 404  # tenant A cannot create into tenant B
        invalid_scene = client.post(
            f"/api/v1/episodes/{episode_a.id}/scenes",
            json={
                "scene_number": 1,
                "script_id": "00000000-0000-0000-0000-000000000001",
                "purpose": "opening",
                "duration_seconds": 10,
            },
        )
        assert invalid_scene.status_code == 422

        scene_payload = {
            "scene_number": 1,
            "script_id": current_script["id"],
            "purpose": "opening",
            "description": "Opening scene",
            "dialogue": "မင်္ဂလာပါ",
            "duration_seconds": 10,
        }
        scene = client.post(f"/api/v1/episodes/{episode_a.id}/scenes", json=scene_payload)
        assert scene.status_code == 201, scene.text
        duplicate = client.post(
            f"/api/v1/episodes/{episode_a.id}/scenes",
            json={**scene_payload, "purpose": "duplicate"},
        )
        assert duplicate.status_code == 409

        # Viewer cannot create scene content.
        active_user = {
            "id": viewer_a.id,
            "email": viewer_a.email,
            "role": "viewer",
            "organization_id": org_a.id,
        }
        active_membership = member_viewer_a
        viewer_scene = client.post(
            f"/api/v1/episodes/{episode_a.id}/scenes",
            json={**scene_payload, "scene_number": 2},
        )
        assert viewer_scene.status_code == 403

        # Cross-tenant list and mutation requests remain hidden.
        active_user = {
            "id": owner_b.id,
            "email": owner_b.email,
            "role": "owner",
            "organization_id": org_b.id,
        }
        active_membership = member_owner_b
        assert client.get(f"/api/v1/episodes/{episode_a.id}/scripts").status_code == 404
        assert client.patch(
            f"/api/v1/scripts/{current_script['id']}",
            json={"content": "cross tenant", "expected_row_version": 1},
        ).status_code == 404
    finally:
        client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
