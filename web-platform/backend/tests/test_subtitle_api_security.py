import json

import pytest

from app.api.dependencies import get_current_membership, get_current_user
from app.db import get_db
from app.main import app
from app.models import (
    Episode,
    Organization,
    OrganizationMembership,
    Series,
    Subtitle,
    User,
)
from client_utils import create_test_client


@pytest.mark.integration
@pytest.mark.security
def test_subtitle_api_enforces_tenant_and_role_boundaries(db_session):
    org_a = Organization(name="Subtitle Tenant A", slug="subtitle-tenant-a")
    org_b = Organization(name="Subtitle Tenant B", slug="subtitle-tenant-b")
    owner_a = User(email="subtitle-owner-a@test.local", role="owner", password_hash="dummy")
    viewer_a = User(email="subtitle-viewer-a@test.local", role="viewer", password_hash="dummy")
    owner_b = User(email="subtitle-owner-b@test.local", role="owner", password_hash="dummy")
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
    series_a = Series(organization_id=org_a.id, title="Subtitle Test Series A")
    series_b = Series(organization_id=org_b.id, title="Subtitle Test Series B")
    db_session.add_all(
        [member_owner_a, member_viewer_a, member_owner_b, series_a, series_b]
    )
    db_session.flush()

    episode_a = Episode(
        organization_id=org_a.id,
        series_id=series_a.id,
        public_id="subtitle_tenant_a_001",
        episode_number=1,
        title="Subtitle Tenant A Episode",
        status="subtitle_review",
    )
    episode_b = Episode(
        organization_id=org_b.id,
        series_id=series_b.id,
        public_id="subtitle_tenant_b_001",
        episode_number=1,
        title="Subtitle Tenant B Episode",
        status="subtitle_review",
    )
    db_session.add_all([episode_a, episode_b])
    db_session.flush()

    draft = Subtitle(
        episode_id=episode_a.id,
        version=1,
        preset="burmese_default",
        cues_json=json.dumps(
            [{"start": 0.0, "end": 2.0, "text": "မြန်မာစာ"}],
            ensure_ascii=False,
        ),
        status="draft",
        is_current=True,
    )
    approved = Subtitle(
        episode_id=episode_b.id,
        version=1,
        preset="burmese_default",
        cues_json=json.dumps(
            [{"start": 0.0, "end": 2.0, "text": "အခြား tenant"}],
            ensure_ascii=False,
        ),
        status="approved",
        is_current=True,
    )
    approved_a = Subtitle(
        episode_id=episode_a.id,
        version=2,
        preset="burmese_default",
        cues_json=json.dumps(
            [{"start": 0.0, "end": 2.0, "text": "အတည်ပြုပြီး"}],
            ensure_ascii=False,
        ),
        status="approved",
        is_current=False,
    )
    db_session.add_all([draft, approved, approved_a])
    db_session.commit()

    original_overrides = dict(app.dependency_overrides)
    active_user = {"id": owner_a.id, "email": owner_a.email, "role": "owner", "organization_id": org_a.id}
    active_membership = member_owner_a
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: active_user
    app.dependency_overrides[get_current_membership] = lambda: active_membership
    client = create_test_client(app)

    try:
        listed = client.get(f"/api/v1/episodes/{episode_a.id}/subtitles")
        assert listed.status_code == 200
        assert {item["id"] for item in listed.json()} == {draft.id, approved_a.id}

        # A viewer can read tenant data but must not mutate subtitle content.
        active_user = {
            "id": viewer_a.id,
            "email": viewer_a.email,
            "role": "viewer",
            "organization_id": org_a.id,
        }
        active_membership = member_viewer_a
        viewer_update = client.patch(
            f"/api/v1/subtitles/{draft.id}",
            json={"cues": [{"start": 0, "end": 2, "text": "ပြင်ဆင်ရန်"}]},
        )
        assert viewer_update.status_code == 403

        # A different tenant must not enumerate the episode or mutate its subtitle.
        active_user = {
            "id": owner_b.id,
            "email": owner_b.email,
            "role": "owner",
            "organization_id": org_b.id,
        }
        active_membership = member_owner_b
        assert client.get(
            f"/api/v1/episodes/{episode_a.id}/subtitles"
        ).status_code == 404
        assert client.patch(
            f"/api/v1/subtitles/{draft.id}",
            json={"cues": [{"start": 0, "end": 2, "text": "cross-tenant"}]},
        ).status_code == 404

        # Approved subtitle content is immutable even for its own tenant.
        active_user = {
            "id": owner_a.id,
            "email": owner_a.email,
            "role": "owner",
            "organization_id": org_a.id,
        }
        active_membership = member_owner_a
        approved_update = client.patch(
            f"/api/v1/subtitles/{approved_a.id}",
            json={"cues": [{"start": 0, "end": 2, "text": "မပြောင်းရ"}]},
        )
        assert approved_update.status_code == 409
    finally:
        client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)
