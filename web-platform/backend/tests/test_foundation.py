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
        patched = client.patch(f"/api/v1/ideas/{idea['id']}", json={"hook": "A test hook", "status": "planned"})
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

        scene = client.post(f"/api/v1/episodes/{episode['id']}/scenes", json={
            "scene_number": 1, "script_id": version.json()["id"], "purpose": "Hook", "dialogue": "ဒီနေ့အကြောင်းအရာက..."
        })
        assert scene.status_code == 201

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
