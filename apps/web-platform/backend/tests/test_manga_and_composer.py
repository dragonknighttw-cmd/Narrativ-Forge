from __future__ import annotations

import pytest
from types import SimpleNamespace
from app.main import app
from app.api.dependencies import get_current_membership, get_current_user
from app.services.manga_engine import MangaEngine, LayoutType, MANGA_SFX_CATALOG
from app.services.video_composer import VideoComposerService, VideoSourceProvider, TransitionType
from tests.client_utils import create_test_client

client = create_test_client(app)


def test_manga_engine_templates():
    templates = MangaEngine.get_layout_templates()
    assert len(templates) >= 4
    template_ids = [t["id"] for t in templates]
    assert LayoutType.WEBTOON_VERTICAL.value in template_ids
    assert LayoutType.YONKOMA_4KOMA.value in template_ids
    assert LayoutType.CINEMATIC_SPLASH.value in template_ids


def test_manga_engine_generate_4koma():
    page = MangaEngine.generate_manga_page(
        title="Epic Mech Awakening",
        story_synopsis="A young pilot awakens the ancient titan mecha in neo-tokyo",
        layout_type=LayoutType.YONKOMA_4KOMA,
        character_names=["Shinji", "Sakura"],
    )
    assert page["total_panels"] == 4
    assert len(page["panels"]) == 4
    assert page["layout_type"] == LayoutType.YONKOMA_4KOMA.value

    # Check panel 3 has twist shout bubble and camera cue
    panel_3 = page["panels"][2]
    assert len(panel_3["bubbles"]) >= 1
    assert panel_3["bubbles"][0]["bubble_type"] == "shout"
    assert panel_3["camera_cue"]["action"] == "zoom_in"


def test_manga_engine_generate_cinematic_splash():
    page = MangaEngine.generate_manga_page(
        title="Final Dimension Slash",
        story_synopsis="Ren confronts the shadow beast with twin energy katanas",
        layout_type=LayoutType.CINEMATIC_SPLASH,
        character_names=["Ren Kurogane", "Shadow Beast"],
    )
    assert page["total_panels"] == 3
    hero_panel = page["panels"][0]
    assert hero_panel["aspect_ratio"] == "16:9"
    assert hero_panel["camera_cue"]["action"] == "camera_shake_and_zoom"


def test_compile_motion_comic():
    page = MangaEngine.generate_manga_page(
        title="Webtoon Prologue",
        story_synopsis="Meeting at the cyber cherry blossom gate",
        layout_type=LayoutType.WEBTOON_VERTICAL,
    )
    motion_comic = MangaEngine.compile_motion_comic_timeline(page)
    assert motion_comic["total_panels"] == 4
    assert len(motion_comic["timeline_cues"]) == 4
    assert motion_comic["total_duration_seconds"] > 0
    assert motion_comic["timeline_cues"][0]["start_time_seconds"] == 0.0


def test_manga_api_routes():
    res_templates = client.get("/api/v1/manga/templates")
    assert res_templates.status_code == 401

    gen_payload = {
        "title": "Bagan Fantasy Chronicles",
        "story_synopsis": "An ancient guardian discovers a floating pagoda in the sky",
        "layout_type": "webtoon_vertical",
        "characters": ["May Myat Noe", "Min Thar"],
    }
    res_gen = client.post("/api/v1/manga/generate", json=gen_payload)
    assert res_gen.status_code == 401


def test_video_composer_api_routes():
    # 1. List providers
    res_prov = client.get("/api/v1/video-composer/providers")
    assert res_prov.status_code == 401

    # 2. Register external clip
    import_payload = {
        "source_url": "https://storage.googleapis.com/sample_videos/kling_clip_01.mp4",
        "provider": "kling_ai",
        "title": "Kling Anime Action Sequence 01",
        "duration_seconds": 6.5,
    }
    res_import = client.post("/api/v1/video-composer/import-clip", json=import_payload)
    assert res_import.status_code == 401


def test_manga_and_video_composer_authorized_routes():
    """The public route guard must not prevent a valid editor workspace flow."""
    app.dependency_overrides[get_current_membership] = lambda: SimpleNamespace(organization_id="test-org")
    app.dependency_overrides[get_current_user] = lambda: {"id": "user-1", "role": "editor", "organization_id": "test-org"}
    try:
        assert client.get("/api/v1/manga/templates").status_code == 200
        manga = client.post("/api/v1/manga/generate", json={
            "title": "Bagan Fantasy Chronicles",
            "story_synopsis": "An ancient guardian discovers a floating pagoda in the sky",
            "layout_type": "webtoon_vertical",
        })
        assert manga.status_code == 200
        assert manga.json()["total_panels"] == 4

        providers = client.get("/api/v1/video-composer/providers")
        assert providers.status_code == 200
        imported = client.post("/api/v1/video-composer/import-clip", json={
            "source_url": "https://example.test/clip.mp4",
            "provider": "kling_ai",
            "title": "Editor clip",
            "duration_seconds": 6.5,
        })
        assert imported.status_code == 200
        assert imported.json()["clip"]["provider"] == "kling_ai"
    finally:
        app.dependency_overrides.clear()
