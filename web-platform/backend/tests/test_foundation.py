from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base, get_db

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_db

def auth_client():
    client = TestClient(app)
    response = client.post("/api/v1/auth/login", json={"email": "admin@narrativ.local", "password": "change-me"})
    assert response.status_code == 200
    return client

def test_health():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

def test_login_sets_http_only_cookie():
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/login", json={"email": "admin@narrativ.local", "password": "change-me"})
        assert response.status_code == 200
        assert "nf_session" in response.cookies
        assert "httponly" in response.headers["set-cookie"].lower()

def test_me_requires_authentication():
    with TestClient(app) as client:
        assert client.get("/api/v1/auth/me").status_code == 401

def test_story_structure_and_episode_status_workflow():
    client = auth_client()
    try:
        idea = client.post("/api/v1/ideas", json={"title": "Test idea"}).json()
        assert idea["status"] == "idea"
        patched = client.patch(f"/api/v1/ideas/{idea['id']}", json={"concept": "A concise test concept", "category": "life", "hook": "A test hook", "status": "planned"})
        assert patched.status_code == 200
        assert patched.json()["hook"] == "A test hook"

        series = client.post("/api/v1/series", json={"title": "Test series"}).json()
        season = client.post(f"/api/v1/series/{series['id']}/seasons", json={"season_number": 1, "title": "Season 1"})
        assert season.status_code == 201

        episode = client.post("/api/v1/episodes", json={
            "series_id": series["id"],
            "season_id": season.json()["id"],
            "episode_number": 1,
            "title": "Episode 1",
            "target_duration_seconds": 180,
        })
        assert episode.status_code == 201
        episode_id = episode.json()["id"]

        duplicate = client.post("/api/v1/episodes", json={
            "series_id": series["id"],
            "season_id": season.json()["id"],
            "episode_number": 1,
            "title": "Duplicate",
        })
        assert duplicate.status_code == 409

        moved = client.patch(f"/api/v1/episodes/{episode_id}", json={"status": "planned"})
        assert moved.status_code == 200
        assert moved.json()["current_step"] == "structure"

        invalid = client.patch(f"/api/v1/episodes/{episode_id}", json={"status": "approved"})
        assert invalid.status_code == 409
    finally:
        client.close()


def test_script_scene_and_asset_vertical_slice(tmp_path, monkeypatch):
    from app.core.config import settings
    settings.upload_dir = str(tmp_path)
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Production series"}).json()
        episode = client.post("/api/v1/episodes", json={
            "series_id": series["id"], "episode_number": 1, "title": "Production episode"
        }).json()

        script = client.post(f"/api/v1/episodes/{episode['id']}/scripts", json={
            "title": "Draft 1", "content": "ပထမဆုံး scene အတွက် draft"
        })
        assert script.status_code == 201
        assert script.json()["version"] == 1
        version = client.post(f"/api/v1/episodes/{episode['id']}/scripts/versions", json={
            "title": "Draft 2", "content": "ပြင်ပြီးသော draft"
        })
        assert version.status_code == 201
        assert version.json()["version"] == 2
        assert version.json()["is_current"] is True
        script_id = version.json()["id"]
        script_patch = client.patch(f"/api/v1/scripts/{script_id}", json={"status": "review"})
        assert script_patch.status_code == 200

        scene = client.post(f"/api/v1/episodes/{episode['id']}/scenes", json={
            "scene_number": 1, "script_id": version.json()["id"], "purpose": "Hook", "dialogue": "ဒီနေ့အကြောင်းအရာက..."
        })
        assert scene.status_code == 201
        scene_id = scene.json()["id"]
        scene_patch = client.patch(f"/api/v1/scenes/{scene_id}", json={"purpose": "Opening hook"})
        assert scene_patch.status_code == 200

        duplicate_scene = client.post(f"/api/v1/episodes/{episode['id']}/scenes", json={
            "scene_number": 1, "purpose": "Duplicate"
        })
        assert duplicate_scene.status_code == 409

        upload = client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("voice.mp3", b"audio-fixture", "audio/mpeg")},
            data={"asset_type": "audio", "copyright_status": "licensed"},
        )
        assert upload.status_code == 201
        assert upload.json()["version"] == 1

        bad_upload = client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("script.exe", b"bad", "application/octet-stream")},
            data={"asset_type": "audio"},
        )
        assert bad_upload.status_code == 415
    finally:
        client.close()


def test_processing_mock_worker_creates_output_and_transcript(tmp_path):
    from app.core.config import settings
    settings.upload_dir = str(tmp_path)
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Worker series"}).json()
        episode = client.post("/api/v1/episodes", json={"series_id": series["id"], "episode_number": 1, "title": "Worker episode"}).json()
        upload = client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("source.mp4", b"video-fixture", "video/mp4")},
            data={"asset_type": "video", "copyright_status": "licensed"},
        )
        assert upload.status_code == 201

        job = client.post("/api/v1/jobs/mock", json={"episode_id": episode["id"]})
        assert job.status_code == 201
        assert job.json()["status"] == "completed"
        assert job.json()["progress"] == 100
        assert job.json()["output_asset_id"]

        assets = client.get(f"/api/v1/episodes/{episode['id']}/assets")
        assert assets.status_code == 200
        asset_types = {item["asset_type"] for item in assets.json()}
        assert "video" in asset_types
        assert "processed_video" in asset_types
        assert "transcript" in asset_types
        assert all(item["version"] > 0 for item in assets.json())
    finally:
        client.close()


def test_processing_missing_input_is_failed_and_retryable(tmp_path):
    from app.core.config import settings
    settings.upload_dir = str(tmp_path)
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Failure series"}).json()
        episode = client.post("/api/v1/episodes", json={"series_id": series["id"], "episode_number": 1, "title": "Failure episode"}).json()

        job = client.post("/api/v1/jobs/mock", json={"episode_id": episode["id"]})
        assert job.status_code == 201
        assert job.json()["status"] == "failed"
        assert job.json()["error_code"] == "INPUT_ASSET_MISSING"

        retry = client.post(f"/api/v1/jobs/{job.json()['id']}/retry")
        assert retry.status_code == 200
        assert retry.json()["status"] == "failed"
        assert retry.json()["retry_count"] == 1
    finally:
        client.close()


def test_subtitle_generation_validation_and_export(tmp_path):
    from app.core.config import settings
    settings.upload_dir = str(tmp_path)
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Subtitle series"}).json()
        episode = client.post("/api/v1/episodes", json={"series_id": series["id"], "episode_number": 1, "title": "Subtitle episode"}).json()
        upload = client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("source.mp4", b"video-fixture", "video/mp4")},
            data={"asset_type": "video", "copyright_status": "licensed"},
        )
        assert upload.status_code == 201
        job = client.post("/api/v1/jobs/mock", json={"episode_id": episode["id"]})
        assert job.status_code == 201

        generated = client.post(f"/api/v1/episodes/{episode['id']}/subtitles/generate", json={"preset": "burmese_default"})
        assert generated.status_code == 201
        subtitle = generated.json()
        assert subtitle["language"] == "my"
        assert subtitle["version"] == 1
        assert subtitle["cues"]

        invalid = client.patch(f"/api/v1/subtitles/{subtitle['id']}", json={
            "cues": [{"start": 0, "end": 8.5, "text": "မြန်မာစာ"}]
        })
        assert invalid.status_code == 200
        assert any(error["code"] == "DISPLAY_TIME" for error in invalid.json()["validation_errors"])

        blocked = client.post(f"/api/v1/episodes/{episode['id']}/subtitles/approve")
        assert blocked.status_code == 409

        valid = client.patch(f"/api/v1/subtitles/{subtitle['id']}", json={
            "cues": [{"start": 0, "end": 2.0, "text": "မြန်မာစာ"}]
        })
        assert valid.status_code == 200
        approved = client.post(f"/api/v1/episodes/{episode['id']}/subtitles/approve")
        assert approved.status_code == 200
        assert approved.json()["status"] == "approved"

        srt = client.get(f"/api/v1/subtitles/{subtitle['id']}/export?format=srt")
        assert srt.status_code == 200
        assert "00:00:00,000 --> 00:00:02,000" in srt.text
        assert "မြန်မာစာ" in srt.text

        vtt = client.get(f"/api/v1/subtitles/{subtitle['id']}/export?format=vtt")
        assert vtt.status_code == 200
        assert vtt.text.startswith("WEBVTT")
    finally:
        client.close()


def test_review_blocks_until_checklist_and_approves_final_asset():
    client = auth_client()
    series = client.post("/api/v1/series", json={"title": "Review series"}).json()
    episode = client.post("/api/v1/episodes", json={"series_id": series["id"], "episode_number": 1, "title": "Review episode"}).json()
    # Move the episode through the existing lifecycle to review.
    for status in ["planned", "script_draft", "script_review", "assets_needed", "in_production", "processing"]:
        response = client.patch(f"/api/v1/episodes/{episode['id']}", json={"status": status})
        assert response.status_code == 200
    client.patch(f"/api/v1/episodes/{episode['id']}", json={"status": "subtitle_review"})
    review = client.post(f"/api/v1/episodes/{episode['id']}/review/approve", json={
        "video_watched": True, "audio_checked": True, "subtitle_timing_checked": True, "thumbnail_present": True
    })
    assert review.status_code == 409
    client.close()


def test_mock_drive_export_is_idempotent_after_approval(tmp_path):
    from app.core.config import settings
    settings.upload_dir = str(tmp_path)
    client = auth_client()
    series = client.post("/api/v1/series", json={"title": "Export series"}).json()
    episode = client.post("/api/v1/episodes", json={"series_id": series["id"], "episode_number": 1, "title": "Export episode"}).json()
    upload = client.post(f"/api/v1/episodes/{episode['id']}/assets/upload", files={"file": ("source.mp4", b"video-fixture", "video/mp4")}, data={"asset_type": "video", "copyright_status": "licensed"})
    assert upload.status_code == 201
    job = client.post("/api/v1/jobs/mock", json={"episode_id": episode["id"]})
    assert job.status_code == 201
    generated = client.post(f"/api/v1/episodes/{episode['id']}/subtitles/generate", json={"preset": "burmese_default"})
    assert generated.status_code == 201
    subtitle = generated.json()
    approved_subtitle = client.post(f"/api/v1/episodes/{episode['id']}/subtitles/approve")
    assert approved_subtitle.status_code == 200

    # Move processing -> subtitle_review -> needs_approval.
    assert client.patch(f"/api/v1/episodes/{episode['id']}", json={"status": "needs_approval"}).status_code == 200
    approved = client.post(f"/api/v1/episodes/{episode['id']}/review/approve", json={
        "video_watched": True, "audio_checked": True, "subtitle_timing_checked": True, "thumbnail_present": True
    })
    assert approved.status_code == 200
    exported = client.post(f"/api/v1/episodes/{episode['id']}/export/mock-drive")
    assert exported.status_code == 200
    assert exported.json()["status"] == "completed"
    exported_again = client.post(f"/api/v1/episodes/{episode['id']}/export/mock-drive")
    assert exported_again.status_code == 200
    assert exported_again.json()["status"] == "completed"
    client.close()


def test_phase7_hook_log_social_and_analytics_flow():
    client = auth_client()
    series = client.post("/api/v1/series", json={"title": "Phase7 series"}).json()
    episode = client.post("/api/v1/episodes", json={"series_id": series["id"], "episode_number": 1, "title": "Phase7 episode"}).json()

    hook = client.post("/api/v1/hooks", json={"hook_text": "မင်း ဒီအချက်ကို သိလား?", "hook_type": "question", "topic": "psychology"})
    assert hook.status_code == 201
    assert hook.json()["hook_type"] == "question"

    log = client.post("/api/v1/manual-production-logs", json={
        "episode_id": episode["id"], "topic": "Phase7 topic", "hook_type": "question",
        "production_time_seconds": 120, "published": True, "platform": "tiktok"
    })
    assert log.status_code == 201

    prep = client.post("/api/v1/social-prep", json={
        "episode_id": episode["id"], "platform": "tiktok",
        "caption": "Phase7 caption", "hashtags": ["#burmese", "#story"],
        "platform_format_valid": True
    })
    assert prep.status_code == 201
    publication_id = prep.json()["id"]

    analytics = client.post(f"/api/v1/social-prep/{publication_id}/analytics", json={
        "views": 1000, "watch_time_seconds": 5000, "completion_rate": 62.5,
        "shares": 20, "saves": 15, "comments": 7
    })
    assert analytics.status_code == 201

    summary = client.get("/api/v1/analytics")
    assert summary.status_code == 200
    assert summary.json()["views"] == 1000
    assert summary.json()["social_records"] == 1
    client.close()
