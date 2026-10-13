import pytest
from app.services.thumbnail_candidate import (
    generate_thumbnail_candidates,
    shortlist_thumbnail_candidates,
    approve_thumbnail_candidate,
)
from app.models import Asset, Episode, Organization, OrganizationMembership, ReviewRecord, Series, User
from client_utils import create_test_client
from app.main import app
from app.db import get_db
from app.api.dependencies import get_current_user, get_current_membership


def test_thumbnail_candidate_generation_and_shortlisting():
    candidates = generate_thumbnail_candidates(
        title="ပုဂံခေတ် ရွှေစည်းခုံ လျှို့ဝှက်ချက်",
        hook="မသိသေးတဲ့ အမှန်တရား",
        category="history",
    )
    # Exactly 10 candidates generated
    assert len(candidates) == 10
    for c in candidates:
        assert c.id.startswith("tc_")
        assert len(c.visual_prompt) > 20
        assert len(c.overlay_text) >= 2
        assert c.score >= 70.0
        assert len(c.reason) > 5

    # Shortlist top 5
    shortlisted = shortlist_thumbnail_candidates(candidates, count=5)
    assert len(shortlisted) == 5
    # Check sorted in descending order of score
    scores = [s.score for s in shortlisted]
    assert scores == sorted(scores, reverse=True)


def test_thumbnail_candidate_human_approval(db_session):
    org = Organization(name="Thumb Org", slug="thumb-org")
    user = User(email="thumb@test.local", role="owner", password_hash="dummy-hash")
    db_session.add(org)
    db_session.add(user)
    db_session.flush()

    membership = OrganizationMembership(organization_id=org.id, user_id=user.id, role="owner")
    db_session.add(membership)

    series = Series(organization_id=org.id, title="Test Series")
    db_session.add(series)
    db_session.flush()

    episode = Episode(
        organization_id=org.id,
        series_id=series.id,
        public_id="nar_thumb_001",
        episode_number=1,
        title="Episode 1 Thumbnail Test",
        status="subtitle_review",
    )
    db_session.add(episode)
    db_session.commit()

    candidates = generate_thumbnail_candidates(episode.title)
    shortlisted = shortlist_thumbnail_candidates(candidates, count=5)
    selected = shortlisted[0]

    result = approve_thumbnail_candidate(
        db=db_session,
        episode_id=episode.id,
        candidate_id=selected.id,
        visual_prompt=selected.visual_prompt,
        overlay_text=selected.overlay_text,
        notes="Human approved via review center",
    )
    assert result["thumbnail_present"] is True
    assert result["approved_thumbnail"]["candidate_id"] == selected.id

    # Verify ReviewRecord checklist has thumbnail_present = True
    record = db_session.query(ReviewRecord).filter(ReviewRecord.episode_id == episode.id).first()
    assert record is not None
    import json
    checklist = json.loads(record.checklist_json)
    assert checklist["thumbnail_present"] is True

    # Verify Asset is created
    thumb_asset = db_session.query(Asset).filter(Asset.episode_id == episode.id, Asset.asset_type == "thumbnail").first()
    assert thumb_asset is not None
    assert thumb_asset.is_final is True


def test_thumbnail_endpoints_api(db_session):
    org = Organization(name="Thumb Org 2", slug="thumb-org-2")
    user = User(email="thumb2@test.local", role="owner", password_hash="dummy-hash")
    db_session.add(org)
    db_session.add(user)
    db_session.flush()

    membership = OrganizationMembership(organization_id=org.id, user_id=user.id, role="owner")
    db_session.add(membership)

    series = Series(organization_id=org.id, title="Test Series 2")
    db_session.add(series)
    db_session.flush()

    episode = Episode(
        organization_id=org.id,
        series_id=series.id,
        public_id="nar_thumb_002",
        episode_number=1,
        title="Episode 2 Thumbnail API Test",
        status="subtitle_review",
    )
    db_session.add(episode)
    db_session.commit()

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: {"id": user.id, "email": user.email, "role": "owner", "organization_id": org.id}
    app.dependency_overrides[get_current_membership] = lambda: membership

    try:
        client = create_test_client(app)

        # GET candidates
        resp = client.get(f"/api/v1/episodes/{episode.id}/review/thumbnails")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_generated"] == 10
        assert len(data["candidates"]) == 10
        assert len(data["shortlisted"]) == 5

        # POST approve 1 candidate
        candidate_to_approve = data["shortlisted"][0]
        resp_app = client.post(
            f"/api/v1/episodes/{episode.id}/review/thumbnails/approve",
            json={
                "candidate_id": candidate_to_approve["id"],
                "visual_prompt": candidate_to_approve["visual_prompt"],
                "overlay_text": candidate_to_approve["overlay_text"],
                "notes": "Approved from modal",
            },
        )
        assert resp_app.status_code == 200
        assert resp_app.json()["thumbnail_present"] is True

        # Re-fetch GET to verify approved status
        resp_after = client.get(f"/api/v1/episodes/{episode.id}/review/thumbnails")
        assert resp_after.status_code == 200
        assert resp_after.json()["approved"]["status"] == "approved"
    finally:
        app.dependency_overrides.clear()
