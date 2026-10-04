import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base, get_db
from app.models import User
from app.services.passwords import hash_password
from client_utils import create_test_client

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)
with TestingSession() as _seed_db:
    if not _seed_db.query(User).filter(User.email == "admin@narrativ.local").first():
        _seed_db.add(User(email="admin@narrativ.local", role="owner", password_hash=hash_password("change-me-123456"), is_active=True))
        _seed_db.commit()

def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_db

def auth_client():
    client = create_test_client(app)
    response = client.post("/api/v1/auth/login", json={"email": "admin@narrativ.local", "password": "change-me-123456"})
    assert response.status_code == 200
    return client

@pytest.mark.integration
def test_health():
    with create_test_client(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

@pytest.mark.integration
@pytest.mark.security
def test_cors_preflight_allows_configured_origin_and_restricts_headers():
    with create_test_client(app) as client:
        response = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,idempotency-key",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
        assert "content-type" in response.headers["access-control-allow-headers"].lower()
        assert "idempotency-key" in response.headers["access-control-allow-headers"].lower()
        assert "x-secret-header" not in response.headers["access-control-allow-headers"].lower()


@pytest.mark.integration
@pytest.mark.security
def test_login_sets_http_only_cookie():
    with create_test_client(app) as client:
        response = client.post("/api/v1/auth/login", json={"email": "admin@narrativ.local", "password": "change-me-123456"})
        assert response.status_code == 200
        assert "nf_session" in response.cookies
        assert "httponly" in response.headers["set-cookie"].lower()

@pytest.mark.integration
@pytest.mark.security
def test_login_rejects_invalid_password():
    with create_test_client(app) as client:
        response = client.post("/api/v1/auth/login", json={"email": "admin@narrativ.local", "password": "wrong-password"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"

@pytest.mark.integration
@pytest.mark.security
def test_me_requires_authentication():
    with create_test_client(app) as client:
        assert client.get("/api/v1/auth/me").status_code == 401

@pytest.mark.integration
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

        moved = client.patch(f"/api/v1/episodes/{episode_id}", json={"status": "planned", "expected_row_version": episode["row_version"]})
        assert moved.status_code == 200
        assert moved.json()["current_step"] == "structure"

        invalid = client.patch(f"/api/v1/episodes/{episode_id}", json={"status": "approved", "expected_row_version": moved.json()["row_version"]})
        assert invalid.status_code == 409
    finally:
        client.close()


@pytest.mark.integration
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
        script_patch = client.patch(f"/api/v1/scripts/{script_id}", json={"status": "review", "expected_row_version": version.json()["row_version"]})
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


@pytest.mark.integration
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


@pytest.mark.integration
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


@pytest.mark.integration
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


@pytest.mark.integration
def test_subtitle_approved_version_is_immutable_and_revision_creates_new_version(tmp_path):
    from app.core.config import settings
    settings.upload_dir = str(tmp_path)
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Subtitle version series"}).json()
        episode = client.post("/api/v1/episodes", json={"series_id": series["id"], "episode_number": 1, "title": "Version episode"}).json()
        upload = client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("source.mp4", b"video-fixture", "video/mp4")},
            data={"asset_type": "video", "copyright_status": "licensed"},
        )
        assert upload.status_code == 201
        assert client.post("/api/v1/jobs/mock", json={"episode_id": episode["id"]}).status_code == 201
        generated = client.post(f"/api/v1/episodes/{episode['id']}/subtitles/generate", json={"preset": "burmese_default"})
        assert generated.status_code == 201
        subtitle = generated.json()

        assert client.patch(
            f"/api/v1/subtitles/{subtitle['id']}",
            json={"cues": [{"start": 0, "end": 2, "text": "မြန်မာစာ"}]},
        ).status_code == 200
        assert client.post(f"/api/v1/episodes/{episode['id']}/subtitles/approve").status_code == 200

        rejected_edit = client.patch(
            f"/api/v1/subtitles/{subtitle['id']}",
            json={"cues": [{"start": 0, "end": 2, "text": "ပြောင်းထားသောစာ"}]},
        )
        assert rejected_edit.status_code == 409

        unchanged = client.get(f"/api/v1/episodes/{episode['id']}/subtitles").json()[0]
        assert unchanged["status"] == "approved"
        assert unchanged["cues"][0]["text"] == "မြန်မာစာ"

        revision = client.post(
            f"/api/v1/subtitles/{subtitle['id']}/versions",
            json={"cues": [{"start": 0, "end": 2, "text": "ပြင်ဆင်ထားသောစာ"}]},
        )
        assert revision.status_code == 201
        assert revision.json()["version"] == 2
        assert revision.json()["status"] == "draft"
        assert revision.json()["is_current"] is True
        assert revision.json()["cues"][0]["text"] == "ပြင်ဆင်ထားသောစာ"
    finally:
        client.close()


@pytest.mark.integration
def test_review_blocks_until_checklist_and_approves_final_asset():
    client = auth_client()
    series = client.post("/api/v1/series", json={"title": "Review series"}).json()
    episode = client.post("/api/v1/episodes", json={"series_id": series["id"], "episode_number": 1, "title": "Review episode"}).json()
    review_state = client.get(f"/api/v1/episodes/{episode['id']}/review")
    assert review_state.status_code == 200
    assert review_state.json()["episode_id"] == episode["id"]
    # Move the episode through the existing lifecycle to review.
    episode_version = episode["row_version"]
    for status in ["planned", "script_draft", "script_review", "assets_needed", "in_production", "processing"]:
        response = client.patch(f"/api/v1/episodes/{episode['id']}", json={"status": status, "expected_row_version": episode_version})
        assert response.status_code == 200
        episode_version = response.json()["row_version"]
    response = client.patch(f"/api/v1/episodes/{episode['id']}", json={"status": "subtitle_review", "expected_row_version": episode_version})
    assert response.status_code == 200
    episode_version = response.json()["row_version"]
    review = client.post(f"/api/v1/episodes/{episode['id']}/review/approve", json={
        "video_watched": True, "audio_checked": True, "subtitle_timing_checked": True, "thumbnail_present": True
    })
    assert review.status_code == 409
    client.close()


@pytest.mark.integration
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
    episode_state = client.get(f"/api/v1/episodes/{episode['id']}").json()
    assert client.patch(f"/api/v1/episodes/{episode['id']}", json={"status": "needs_approval", "expected_row_version": episode_state["row_version"]}).status_code == 200
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


@pytest.mark.integration
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


@pytest.mark.unit
@pytest.mark.security
def test_upload_safety_rejects_mime_extension_mismatch_and_sanitizes_filename():
    from app.api.routes.assets import safe_filename, validate_upload
    assert safe_filename("../../secret.mp4") == "secret.mp4"
    assert safe_filename("bad name?.mp4") == "bad_name_.mp4"
    with pytest.raises(Exception):
        validate_upload("clip.exe", "video/mp4", "video")
    with pytest.raises(Exception):
        validate_upload("clip.mp4", "image/png", "video")


@pytest.mark.integration
def test_real_processing_pipeline_creates_render_and_whisper_assets(monkeypatch, tmp_path):
    from pathlib import Path
    from app.models import Asset, Episode, ProcessingJob, Series
    from app.services import real_processing

    db = TestingSession()
    source = tmp_path / "source.mp4"
    source.write_bytes(b"fixture-video")
    series = Series(title="Real processing test")
    db.add(series)
    db.flush()
    episode = Episode(
        public_id="NF-REAL-TEST",
        series_id=series.id,
        episode_number=1,
        title="Real processing",
        status="in_production",
        current_step="processing",
    )
    db.add(episode)
    db.flush()
    asset = Asset(
        episode_id=episode.id,
        asset_type="video",
        original_filename="source.mp4",
        storage_provider="local",
        local_path=str(source),
        mime_type="video/mp4",
        file_size_bytes=source.stat().st_size,
        version=1,
        status="uploaded",
    )
    db.add(asset)
    db.flush()
    job = ProcessingJob(episode_id=episode.id, job_type="real_processing", status="running", input_asset_id=asset.id)
    db.add(job)
    db.commit()

    seen_timeouts = []

    def fake_run(command, *, timeout):
        seen_timeouts.append(timeout)
        if "ffprobe" in command[0]:
            return type("Result", (), {"stdout": '{"streams":[{"codec_type":"video","width":1080,"height":1920},{"codec_type":"audio"}],"format":{"duration":"2.0"}}', "stderr": ""})()
        output = Path(command[-1])
        if "ffmpeg" in command[0]:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
        else:
            output_dir = Path(command[command.index("--output_dir") + 1])
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "source.json").write_text(
                '{"language":"my","segments":[{"start":0,"end":2,"text":"မြန်မာ"}]}',
                encoding="utf-8",
            )
        return type("Result", (), {"stdout": "", "stderr": ""})()

    monkeypatch.setattr(real_processing, "_run", fake_run)
    monkeypatch.setattr(real_processing.settings, "upload_dir", str(tmp_path / "uploads"))
    result = real_processing.run_real_job(job.id, db, already_claimed=True)

    assert result.status == "completed"
    assert db.get(Episode, episode.id).status == "subtitle_review"
    output = db.get(Asset, result.output_asset_id)
    assert output.asset_type == "processed_video"
    assert seen_timeouts == [real_processing.settings.processing_timeout_seconds] * 3
    assert Path(output.local_path).read_bytes() == b"rendered"
    transcript = db.query(Asset).filter(Asset.episode_id == episode.id, Asset.asset_type == "transcript").one()
    assert "မြန်မာ" in Path(transcript.local_path).read_text(encoding="utf-8")


@pytest.mark.integration
@pytest.mark.security
def test_session_cookie_is_signed_and_tampering_is_rejected():
    from app.api.dependencies import issue_session
    with create_test_client(app) as client:
        token = issue_session("admin@narrativ.local")
        assert token != "dev-session"
        client.cookies.set("nf_session", token)
        assert client.get("/api/v1/auth/me").status_code == 200
        client.cookies.set("nf_session", token[:-1] + ("A" if token[-1] != "A" else "B"))
        assert client.get("/api/v1/auth/me").status_code == 401


@pytest.mark.integration
@pytest.mark.security
def test_security_headers_are_present():
    with create_test_client(app) as client:
        response = client.get("/api/v1/health")
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["referrer-policy"] == "same-origin"
        assert "permissions-policy" in response.headers


@pytest.mark.integration
def test_google_drive_export_failure_is_resumable(monkeypatch, tmp_path):
    import httpx
    from app.core.config import settings
    from app.api.routes import google_drive

    settings.upload_dir = str(tmp_path)
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Drive retry series"}).json()
        episode = client.post("/api/v1/episodes", json={
            "series_id": series["id"], "episode_number": 1, "title": "Drive retry episode"
        }).json()
        upload = client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("source.mp4", b"video-fixture", "video/mp4")},
            data={"asset_type": "video", "copyright_status": "licensed"},
        )
        assert upload.status_code == 201
        assert client.post("/api/v1/jobs/mock", json={"episode_id": episode["id"]}).status_code == 201
        subtitle = client.post(
            f"/api/v1/episodes/{episode['id']}/subtitles/generate",
            json={"preset": "burmese_default"},
        ).json()
        assert client.patch(
            f"/api/v1/subtitles/{subtitle['id']}",
            json={"cues": [{"start": 0, "end": 2, "text": "မြန်မာစာ"}]},
        ).status_code == 200
        assert client.post(f"/api/v1/episodes/{episode['id']}/subtitles/approve").status_code == 200
        assert client.patch(f"/api/v1/episodes/{episode['id']}", json={"status": "needs_approval"}).status_code == 200
        approved = client.post(f"/api/v1/episodes/{episode['id']}/review/approve", json={
            "video_watched": True, "audio_checked": True,
            "subtitle_timing_checked": True, "thumbnail_present": True,
        })
        assert approved.status_code == 200

        async def fake_access_token(email, db):
            return "fake-token"

        class FakeResponse:
            def __init__(self, payload=None):
                self._payload = payload or {}
            def raise_for_status(self):
                return None
            def json(self):
                return self._payload

        class FakeClient:
            failed_once = False
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                return False
            async def post(self, url, **kwargs):
                if not FakeClient.failed_once:
                    FakeClient.failed_once = True
                    raise httpx.ReadTimeout("forced export failure")
                if "upload/drive" not in url:
                    return FakeResponse({"id": "folder-1"})
                name = "video-1"
                body = kwargs.get("content", b"")
                if b"application/json" in body and b"export-manifest" in body:
                    name = "manifest-1"
                elif b"application/x-subrip" in body:
                    name = "subtitle-1"
                return FakeResponse({"id": name})
            async def get(self, url, **kwargs):
                return FakeResponse({"files": []})

        monkeypatch.setattr(google_drive, "access_token_for", fake_access_token)
        monkeypatch.setattr(httpx, "AsyncClient", lambda *args, **kwargs: FakeClient())

        first = client.post(f"/api/v1/episodes/{episode['id']}/export/google-drive")
        assert first.status_code == 502
        history = client.get(f"/api/v1/episodes/{episode['id']}/export/history")
        assert history.status_code == 200
        assert history.json()[0]["status"] == "failed"

        second = client.post(f"/api/v1/episodes/{episode['id']}/export/google-drive")
        assert second.status_code == 200
        assert second.json()["status"] == "completed"
        assert second.json()["manifest"]["folder_id"] == "folder-1"
        assert second.json()["manifest"]["video_file_id"] == "video-1"
    finally:
        client.close()


@pytest.mark.integration
def test_full_production_integration_flow(tmp_path):
    from app.core.config import settings
    settings.upload_dir = str(tmp_path)
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Full flow series"}).json()
        season = client.post(
            f"/api/v1/series/{series['id']}/seasons",
            json={"season_number": 1, "title": "Season 1"},
        ).json()
        episode = client.post("/api/v1/episodes", json={
            "series_id": series["id"], "season_id": season["id"],
            "episode_number": 1, "title": "Full flow episode",
        }).json()

        assert client.post(
            f"/api/v1/episodes/{episode['id']}/scripts",
            json={"title": "Draft", "content": "Hook\nBody\nClose"},
        ).status_code == 201
        assert client.post(
            f"/api/v1/episodes/{episode['id']}/scenes",
            json={"scene_number": 1, "purpose": "Hook", "dialogue": "မင်း ဒီအချက်ကို သိလား?"},
        ).status_code == 201

        upload = client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("source.mp4", b"video-fixture", "video/mp4")},
            data={"asset_type": "video", "copyright_status": "licensed"},
        )
        assert upload.status_code == 201
        assert client.post("/api/v1/jobs/mock", json={"episode_id": episode["id"]}).status_code == 201

        subtitle = client.post(
            f"/api/v1/episodes/{episode['id']}/subtitles/generate",
            json={"preset": "burmese_default"},
        ).json()
        assert client.patch(
            f"/api/v1/subtitles/{subtitle['id']}",
            json={"cues": [{"start": 0, "end": 2, "text": "မြန်မာစာ"}]},
        ).status_code == 200
        assert client.post(f"/api/v1/episodes/{episode['id']}/subtitles/approve").status_code == 200
        assert client.patch(f"/api/v1/episodes/{episode['id']}", json={"status": "needs_approval"}).status_code == 200
        assert client.post(f"/api/v1/episodes/{episode['id']}/review/approve", json={
            "video_watched": True, "audio_checked": True,
            "subtitle_timing_checked": True, "thumbnail_present": True,
        }).status_code == 200

        exported = client.post(f"/api/v1/episodes/{episode['id']}/export/mock-drive")
        assert exported.status_code == 200
        assert exported.json()["status"] == "completed"
        history = client.get(f"/api/v1/episodes/{episode['id']}/export/history")
        assert history.status_code == 200
        assert history.json()[0]["status"] == "completed"

        log = client.post("/api/v1/manual-production-logs", json={
            "episode_id": episode["id"], "topic": "Integration topic",
            "hook_type": "question", "production_time_seconds": 120,
            "published": True, "platform": "tiktok",
        })
        assert log.status_code == 201
        assert client.get("/api/v1/analytics").status_code == 200
    finally:
        client.close()


@pytest.mark.integration
def test_approval_and_export_create_audit_events(tmp_path):
    from app.core.config import settings
    settings.upload_dir = str(tmp_path)
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Audit series"}).json()
        episode = client.post("/api/v1/episodes", json={"series_id": series["id"], "episode_number": 1, "title": "Audit episode"}).json()
        assert client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("source.mp4", b"video-fixture", "video/mp4")},
            data={"asset_type": "video", "copyright_status": "licensed"},
        ).status_code == 201
        assert client.post("/api/v1/jobs/mock", json={"episode_id": episode["id"]}).status_code == 201
        subtitle = client.post(f"/api/v1/episodes/{episode['id']}/subtitles/generate", json={"preset": "burmese_default"}).json()
        assert client.patch(f"/api/v1/subtitles/{subtitle['id']}", json={"cues": [{"start": 0, "end": 2, "text": "မြန်မာစာ"}]}).status_code == 200
        assert client.post(f"/api/v1/episodes/{episode['id']}/subtitles/approve").status_code == 200
        assert client.patch(f"/api/v1/episodes/{episode['id']}", json={"status": "needs_approval"}).status_code == 200
        assert client.post(f"/api/v1/episodes/{episode['id']}/review/approve", json={
            "video_watched": True, "audio_checked": True,
            "subtitle_timing_checked": True, "thumbnail_present": True,
        }).status_code == 200
        assert client.post(f"/api/v1/episodes/{episode['id']}/export/mock-drive").status_code == 200
        events = client.get("/api/v1/audit?limit=10")
        assert events.status_code == 200
        actions = {event["action"] for event in events.json()}
        assert "episode.approved" in actions
        assert "episode.exported" in actions
    finally:
        client.close()


@pytest.mark.integration
@pytest.mark.security
def test_production_rbac_invite_and_role_authority():
    client = auth_client()
    try:
        invited = client.post("/api/v1/auth/invite", json={
            "email": "editor@example.com",
            "password": "strong-editor-password",
            "role": "editor",
        })
        assert invited.status_code == 200
        assert invited.json()["role"] == "editor"

        client.post("/api/v1/auth/logout")
        login = client.post("/api/v1/auth/login", json={
            "email": "editor@example.com",
            "password": "strong-editor-password",
        })
        assert login.status_code == 200
        assert login.json()["user"]["role"] == "editor"

        assert client.post("/api/v1/ideas", json={"title": "editor idea"}).status_code == 201
        assert client.post("/api/v1/series", json={"title": "editor series"}).status_code == 201

        forbidden = client.get("/api/v1/audit")
        assert forbidden.status_code == 403
    finally:
        client.close()


@pytest.mark.unit
def test_storage_abstraction_upload_download_delete_and_asset_metadata(tmp_path, monkeypatch):
    from app.services.storage import LocalStorageProvider, build_object_key, sha256_file

    provider = LocalStorageProvider(str(tmp_path / "storage"))
    source = tmp_path / "source.bin"
    source.write_bytes(b"storage-fixture")
    key = build_object_key("episode-1", 3, "source.mp4", "video")
    stored = provider.upload_file(source, key, "video/mp4")

    assert stored.provider == "local"
    assert stored.object_key == key
    assert stored.size_bytes == source.stat().st_size
    assert stored.checksum_sha256 == sha256_file(source)
    assert provider.exists(key)

    destination = tmp_path / "downloaded.bin"
    downloaded = provider.download_file(key, destination)
    assert destination.read_bytes() == source.read_bytes()
    assert downloaded.checksum_sha256 == stored.checksum_sha256

    provider.delete(key)
    assert not provider.exists(key)


@pytest.mark.integration
def test_upload_persists_storage_object_metadata(tmp_path):
    from app.core.config import settings

    settings.upload_dir = str(tmp_path)
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Storage metadata"}).json()
        episode = client.post("/api/v1/episodes", json={
            "series_id": series["id"], "episode_number": 1, "title": "Storage episode"
        }).json()
        response = client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("source.mp4", b"storage-video", "video/mp4")},
            data={"asset_type": "video", "copyright_status": "licensed"},
        )
        assert response.status_code == 201
        asset = response.json()
        assert asset["storage_provider"] == "local"
        assert asset["object_key"].startswith(f"episodes/{episode['id']}/assets/v1/video/")
        assert len(asset["checksum_sha256"]) == 64
        assert asset["file_size_bytes"] == len(b"storage-video")
        download = client.get(f"/api/v1/assets/{asset['id']}/download")
        assert download.status_code == 200
        assert download.content == b"storage-video"
    finally:
        client.close()


@pytest.mark.integration
@pytest.mark.security
def test_production_storage_gate_requires_storj_configuration(monkeypatch):
    from app.core.config import Settings

    settings_obj = Settings(
        app_env="production",
        database_url="sqlite:///./gate.db",
        session_secret="x" * 40,
        session_cookie_secure=True,
        cors_origins="https://app.example.com",
        trusted_hosts="api.example.com",
        oauth_encryption_key="y" * 32,
        storage_provider="storj",
    )
    try:
        settings_obj.validate_runtime()
        assert False, "expected missing Storj configuration to be rejected"
    except RuntimeError as exc:
        assert "Storj storage configuration missing" in str(exc)


@pytest.mark.integration
def test_storj_storage_integration_roundtrip_when_configured(tmp_path):
    import os
    from app.services.storage import get_storage

    required = [
        os.getenv("STORJ_ACCESS_KEY_ID"),
        os.getenv("STORJ_SECRET_ACCESS_KEY"),
        os.getenv("STORJ_BUCKET_NAME"),
        os.getenv("STORJ_REGION"),
    ]
    if not all(required):
        pytest.skip("Storj integration credentials are not configured")

    provider = get_storage("storj")
    source = tmp_path / "storj-fixture.bin"
    source.write_bytes(b"narrativ-forge-storj-integration")
    key = f"tests/{uuid4().hex}/fixture.bin"

    try:
        stored = provider.upload_file(source, key, "application/octet-stream")
        assert stored.provider == "storj"
        assert stored.size_bytes == source.stat().st_size
        assert provider.exists(key)

        destination = tmp_path / "downloaded.bin"
        downloaded = provider.download_file(key, destination)
        assert destination.read_bytes() == source.read_bytes()
        assert downloaded.checksum_sha256 == stored.checksum_sha256
    finally:
        provider.delete(key)
        assert not provider.exists(key)


@pytest.mark.integration
@pytest.mark.security
def test_viewer_is_read_only_for_production_mutations():
    client = auth_client()
    try:
        invited = client.post("/api/v1/auth/invite", json={
            "email": "viewer@example.com",
            "password": "strong-viewer-password",
            "role": "viewer",
        })
        assert invited.status_code == 200

        client.post("/api/v1/auth/logout")
        login = client.post("/api/v1/auth/login", json={
            "email": "viewer@example.com",
            "password": "strong-viewer-password",
        })
        assert login.status_code == 200
        assert login.json()["user"]["role"] == "viewer"

        assert client.post("/api/v1/ideas", json={"title": "blocked"}).status_code == 403
        assert client.post("/api/v1/series", json={"title": "blocked"}).status_code == 403
        assert client.post("/api/v1/jobs/mock", json={"episode_id": "missing"}).status_code == 403
        assert client.post("/api/v1/hooks", json={
            "hook_text": "blocked", "hook_type": "question"
        }).status_code == 403
    finally:
        client.close()


@pytest.mark.unit
def test_subtitle_quality_gate_enforces_source_requirements():
    from app.services.subtitles import validate_cues

    errors = validate_cues([
        {"start": 0, "end": 0.5, "text": "မြန်မာ"},
        {"start": 0.4, "end": 8, "text": "English only"},
    ])
    codes = {error["code"] for error in errors}
    assert "DISPLAY_TIME" in codes
    assert "CUE_OVERLAP" in codes
    assert "BURMESE_TEXT_REQUIRED" in codes


@pytest.mark.unit
def test_publication_metadata_validation():
    from app.api.routes.production_intelligence import validate_publication_payload

    assert validate_publication_payload("tiktok", "caption", ["#မြန်မာ"]) == []
    assert "Unsupported platform" in validate_publication_payload("unknown", "caption", [])
    assert "Caption is required" in validate_publication_payload("tiktok", "", [])


@pytest.mark.unit
def test_auto_mode_adapter_produces_deterministic_plan():
    from app.services.ai_adapter import MockAIAdapter

    plan = MockAIAdapter().create_content_plan(idea="စမ်းသပ်အကြောင်းအရာ")
    assert plan.hook
    assert plan.script
    assert len(plan.scenes) >= 1


@pytest.mark.integration
def test_production_intelligence_crud_and_analytics():
    client = auth_client()
    try:
        hook = client.post("/api/v1/hooks", json={"hook_text": "မေးခွန်း hook", "hook_type": "question"})
        assert hook.status_code == 201
        hook_id = hook.json()["id"]
        assert client.patch(f"/api/v1/hooks/{hook_id}", json={"hook_text": "ပြင်ထားသော hook", "hook_type": "question"}).status_code == 200

        log = client.post("/api/v1/manual-production-logs", json={
            "topic": "Test topic", "hook_type": "question", "duration_seconds": 30,
            "published": True, "views": 100,
        })
        assert log.status_code == 201
        log_id = log.json()["id"]
        assert client.patch(f"/api/v1/manual-production-logs/{log_id}", json={
            "topic": "Updated topic", "hook_type": "question", "views": 150,
        }).status_code == 200

        summary = client.get("/api/v1/analytics")
        assert summary.status_code == 200
        assert "by_hook_type" in summary.json()
    finally:
        client.close()


@pytest.mark.integration
def test_auto_mode_creates_script_versions_and_requires_source_video():
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Auto series"}).json()
        episode = client.post("/api/v1/episodes", json={
            "series_id": series["id"], "episode_number": 1, "title": "Auto episode"
        }).json()
        episode_id = episode["id"]

        first = client.post(f"/api/v1/auto/episodes/{episode_id}/plan", json={"idea": "ပထမအကြောင်းအရာ"})
        assert first.status_code == 200
        assert len(first.json()["scenes"]) == 2

        second = client.post(f"/api/v1/auto/episodes/{episode_id}/plan", json={"idea": "ဒုတိယအကြောင်းအရာ"})
        assert second.status_code == 200
        assert second.json()["script"]["version"] == 2

        blocked = client.post(f"/api/v1/auto/episodes/{episode_id}/run", json={"idea": "Run"})
        assert blocked.status_code == 409
    finally:
        client.close()


@pytest.mark.integration
def test_historical_script_version_is_immutable():
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Immutable script series"}).json()
        episode = client.post(
            "/api/v1/episodes",
            json={"series_id": series["id"], "episode_number": 1, "title": "Immutable episode"},
        )
        assert episode.status_code == 201
        ep = episode.json()
        first = client.post(
            f"/api/v1/episodes/{ep['id']}/scripts",
            json={"title": "v1", "content": "original"},
        )
        assert first.status_code == 201
        second = client.post(
            f"/api/v1/episodes/{ep['id']}/scripts/versions",
            json={"title": "v2", "content": "new"},
        )
        assert second.status_code == 201
        old = first.json()
        response = client.patch(
            f"/api/v1/scripts/{old['id']}",
            json={"content": "tampered", "expected_row_version": old["row_version"]},
        )
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "HISTORICAL_SCRIPT_IMMUTABLE"
    finally:
        client.close()


@pytest.mark.integration
def test_export_state_compare_and_set_blocks_second_export_claim():
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Export CAS series"}).json()
        episode = client.post(
            "/api/v1/episodes",
            json={"series_id": series["id"], "episode_number": 1, "title": "Export CAS episode"},
        ).json()
        moved = client.patch(
            f"/api/v1/episodes/{episode['id']}",
            json={"status": "approved", "expected_row_version": episode["row_version"]},
        )
        assert moved.status_code == 200

        from app.db import SessionLocal
        from app.api.routes.export import _claim_export

        db = SessionLocal()
        try:
            _claim_export(db, episode["id"], expected_status="approved")
            with pytest.raises(Exception) as exc_info:
                _claim_export(db, episode["id"], expected_status="approved")
            assert getattr(exc_info.value, "status_code", None) == 409
        finally:
            db.close()
    finally:
        client.close()
