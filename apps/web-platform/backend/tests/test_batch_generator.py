import pytest
from app.services.hook_engineering import (
    CANONICAL_HOOK_TYPES,
    CANONICAL_HOOK_TEMPLATES,
    generate_hook_candidates,
    generate_canonical_hook_candidates,
    canonicalize_hook_type,
)
from app.services.batch_generator import (
    generate_5_episode_batch,
    commit_batch_episodes,
)
from app.models import Episode, Series


def test_canonical_hook_engineering_all_eight_families():
    candidates = generate_canonical_hook_candidates("မြန်မာ့ယဉ်ကျေးမှု အမွေအနှစ်များ")
    assert len(candidates) == 8
    hook_types = {item.hook_type for item in candidates}
    assert hook_types == set(CANONICAL_HOOK_TYPES)
    for c in candidates:
        assert len(c.text) > 10
        assert c.score > 0.0


def test_canonicalize_hook_type_mapping():
    assert canonicalize_hook_type("curiosity_gap") == "mystery"
    assert canonicalize_hook_type("bold_claim") == "shock"
    assert canonicalize_hook_type("story") == "personal_story"
    assert canonicalize_hook_type("problem_solution") == "warning"
    assert canonicalize_hook_type("contrast") == "contrarian"
    assert canonicalize_hook_type("challenge") == "cliffhanger"
    assert canonicalize_hook_type("mystery") == "mystery"
    assert canonicalize_hook_type("number") == "number"


def test_generate_5_episode_batch_plan():
    plan = generate_5_episode_batch(theme="ပုဂံခေတ် လျှို့ဝှက်ချက် ၅ ခု", category="history")
    assert plan.theme == "ပုဂံခေတ် လျှို့ဝှက်ချက် ၅ ခု"
    assert plan.category == "history"
    assert len(plan.episodes) == 5

    # Check episode numbers 1..5
    numbers = [ep.episode_number for ep in plan.episodes]
    assert numbers == [1, 2, 3, 4, 5]

    # Verify each episode has valid Burmese fields
    for ep in plan.episodes:
        assert "အပိုင်း" in ep.title
        assert len(ep.hook) > 10
        assert ep.hook_family in CANONICAL_HOOK_TYPES
        assert len(ep.synopsis) > 20
        assert len(ep.cliffhanger) > 10
        assert len(ep.scenes) == 3
        assert sum(s["duration_seconds"] for s in ep.scenes) == ep.target_duration_seconds


def test_commit_batch_episodes_persists_to_db(db_session):
    plan = generate_5_episode_batch(theme="မန္တလေးမြို့ သမိုင်း", category="culture")
    series, episodes = commit_batch_episodes(
        db=db_session,
        organization_id="test_org_batch",
        plan=plan,
    )
    assert series.id is not None
    assert series.title.startswith("မန္တလေးမြို့ သမိုင်း")
    assert len(episodes) == 5

    for idx, ep in enumerate(episodes, start=1):
        assert ep.episode_number == idx
        assert ep.series_id == series.id
        assert ep.organization_id == "test_org_batch"
        assert ep.status == "planned"
        assert len(ep.scripts) >= 1
        assert len(ep.scenes) >= 3


def test_api_batch_generate_preview_and_commit(db_session):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.db import get_db
    from app.api.dependencies import get_current_user, get_current_membership
    from app.models import Organization, OrganizationMembership, User

    org = Organization(name="Batch Org", slug="batch-org")
    user = User(email="batch@test.local", role="owner", password_hash="dummy-hash")
    db_session.add(org)
    db_session.add(user)
    db_session.flush()
    membership = OrganizationMembership(organization_id=org.id, user_id=user.id, role="owner")
    db_session.add(membership)
    db_session.commit()

    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: {"id": user.id, "email": user.email, "role": "owner", "organization_id": org.id}
    app.dependency_overrides[get_current_membership] = lambda: membership

    try:
        from client_utils import create_test_client
        client = create_test_client(app)
        # Preview without commit
        resp_preview = client.post(
            "/api/v1/auto/batch-generate",
            json={"theme": "AI နည်းပညာနှင့် မြန်မာနိုင်ငံ", "category": "technology", "commit": False},
        )
        assert resp_preview.status_code == 200
        data_prev = resp_preview.json()
        assert data_prev["committed"] is False
        assert len(data_prev["plan"]["episodes"]) == 5

        # Commit
        resp_commit = client.post(
            "/api/v1/auto/batch-generate",
            json={"theme": "AI နည်းပညာနှင့် မြန်မာနိုင်ငံ", "category": "technology", "commit": True},
        )
        assert resp_commit.status_code == 200
        data_comm = resp_commit.json()
        assert data_comm["committed"] is True
        assert len(data_comm["episodes"]) == 5
        assert data_comm["series"]["title"].startswith("AI နည်းပညာနှင့် မြန်မာနိုင်ငံ")
    finally:
        app.dependency_overrides.clear()

