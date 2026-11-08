from __future__ import annotations

import pytest
from app.main import app
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
    assert res_templates.status_code == 200
    assert len(res_templates.json()) >= 4

    res_sfx = client.get("/api/v1/manga/sfx-catalog")
    assert res_sfx.status_code == 200
    catalog = res_sfx.json()
    assert any(s["japanese"] == "ドドド" for s in catalog)
    assert any(s["burmese"] == "ဒုန်း!" for s in catalog)

    gen_payload = {
        "title": "Bagan Fantasy Chronicles",
        "story_synopsis": "An ancient guardian discovers a floating pagoda in the sky",
        "layout_type": "webtoon_vertical",
        "characters": ["May Myat Noe", "Min Thar"],
    }
    res_gen = client.post("/api/v1/manga/generate", json=gen_payload)
    assert res_gen.status_code == 200
    page_data = res_gen.json()
    assert page_data["total_panels"] == 4

    export_res = client.post("/api/v1/manga/motion-comic/export", json={"manga_page": page_data})
    assert export_res.status_code == 200
    assert export_res.json()["total_duration_seconds"] > 0


def test_video_composer_api_routes():
    # 1. List providers
    res_prov = client.get("/api/v1/video-composer/providers")
    assert res_prov.status_code == 200
    provider_ids = [p["id"] for p in res_prov.json()]
    assert "runway_gen3" in provider_ids
    assert "kling_ai" in provider_ids
    assert "openai_sora" in provider_ids

    # 2. Register external clip
    import_payload = {
        "source_url": "https://storage.googleapis.com/sample_videos/kling_clip_01.mp4",
        "provider": "kling_ai",
        "title": "Kling Anime Action Sequence 01",
        "duration_seconds": 6.5,
    }
    res_import = client.post("/api/v1/video-composer/import-clip", json=import_payload)
    assert res_import.status_code == 200
    imported_clip = res_import.json()["clip"]
    assert imported_clip["provider"] == "kling_ai"
    assert imported_clip["duration_seconds"] == 6.5

    # 3. Build multi-track timeline
    tl_payload = {
        "title": "Anime Battle Ep 1 Final Cut",
        "video_clips": [
            imported_clip,
            {
                "id": "clip_2",
                "source_url": "https://storage.googleapis.com/sample_videos/runway_clip_02.mp4",
                "provider": "runway_gen3",
                "title": "Runway Mech Explosion",
                "duration_seconds": 4.0,
                "speed_factor": 1.0,
            },
        ],
        "bgm_track_url": "https://cdn.pixabay.com/audio/epic_battle_bgm.mp3",
        "bgm_volume_percent": 25.0,
        "dubbing_cues": [
            {
                "id": "dub_1",
                "audio_url": "/storage/audio/shinji_line1.mp3",
                "start_time_seconds": 1.0,
                "duration_seconds": 2.5,
                "voice_binding": {"voice_id": "ja-JP-KeitaNeural", "actor": "Shinji"},
            }
        ],
        "subtitles": [
            {
                "id": "sub_1",
                "text": "Ikuzo, Titan Unit Zero!",
                "start_time_seconds": 1.0,
                "end_time_seconds": 3.5,
                "speaker": "Shinji",
                "style": "anime_pop",
            }
        ],
        "target_aspect_ratio": "9:16",
    }
    res_tl = client.post("/api/v1/video-composer/timeline", json=tl_payload)
    assert res_tl.status_code == 200
    timeline = res_tl.json()
    assert timeline["total_duration_seconds"] == 10.5  # 6.5 + 4.0
    assert len(timeline["tracks"]["video"]) == 2
    assert len(timeline["tracks"]["audio"]) == 2  # 1 BGM + 1 Dubbing
    assert len(timeline["tracks"]["subtitles"]) == 1

    # 4. Render FFmpeg Spec
    res_ffmpeg = client.post("/api/v1/video-composer/render-ffmpeg-spec", json=tl_payload)
    assert res_ffmpeg.status_code == 200
    ffmpeg_data = res_ffmpeg.json()
    assert ffmpeg_data["status"] == "ready"
    assert "1080x1920" in ffmpeg_data["resolution"]
    assert "ffmpeg" in ffmpeg_data["ffmpeg_command"]
