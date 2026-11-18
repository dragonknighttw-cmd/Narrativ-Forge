import pytest
from app.services.creative_studio import CreativeStudioService


def test_reference_analysis_service():
    result = CreativeStudioService.analyze_reference(
        title="Epic Battle Scene Reference",
        file_url="https://example.com/ref.mp4",
        duration_seconds=90.0,
        user_notes="High paced action combat",
    )
    assert result["title"] == "Epic Battle Scene Reference"
    assert result["shot_count"] > 0
    assert "Hyper-Paced Action" in result["style_tags"]
    assert "detected_bpm" in result["music_rhythm"]
    assert result["color_palette"]["dominant_mood"] != ""


def test_footage_scanning_service():
    result = CreativeStudioService.scan_footage(
        filename="hero_walking_neon.mp4",
        file_url="https://example.com/raw1.mp4",
        duration_seconds=20.0,
    )
    assert result["filename"] == "hero_walking_neon.mp4"
    assert len(result["scenes"]) > 0
    assert result["quality_score"] > 80.0
    assert result["selected_highlight"] is True


def test_creative_concepts_generation():
    concepts = CreativeStudioService.generate_creative_concepts(
        episode_title="Night of the Phantom",
        logline="A lone cyber detective hunts a rogue AI through Yangon back-alleys.",
        target_duration_seconds=180,
    )
    assert len(concepts) == 3
    types = [c["concept_type"] for c in concepts]
    assert "epic_cinematic" in types
    assert "fast_paced_social" in types
    assert "emotional_storytelling" in types
    for c in concepts:
        assert len(c["emotional_arc"]) > 0
        assert len(c["shot_decisions"]) > 0


def test_music_and_sfx_catalogs():
    music = CreativeStudioService.get_curated_music_catalog()
    assert len(music) >= 4
    for track in music:
        assert track["bpm"] > 0
        assert len(track["beat_drops"]) > 0

    sfx = CreativeStudioService.get_curated_sfx_catalog()
    assert len(sfx) >= 4
    categories = [s["category"] for s in sfx]
    assert "cinematic_impact" in categories
    assert "whoosh_transition" in categories


def test_quality_control_evaluation():
    # Good timeline
    good_timeline = {
        "video_track": [
            {"clip_id": "c1", "start_time": 0.0, "end_time": 3.0},
            {"clip_id": "c2", "start_time": 3.0, "end_time": 6.5},
        ],
        "voice_track": [{"start_time": 0.0, "end_time": 6.5}],
        "subtitle_track": [{"start_time": 0.0, "end_time": 6.5}],
    }
    qc = CreativeStudioService.evaluate_quality_control(good_timeline)
    assert qc["passed"] is True
    assert qc["black_frames_detected"] == 0

    # Bad timeline with gap (black frame)
    gap_timeline = {
        "video_track": [
            {"clip_id": "c1", "start_time": 0.0, "end_time": 3.0},
            {"clip_id": "c2", "start_time": 3.5, "end_time": 6.5},  # 0.5s gap
        ]
    }
    qc_gap = CreativeStudioService.evaluate_quality_control(gap_timeline)
    assert qc_gap["black_frames_detected"] == 1
    assert any(i["type"] == "black_frame_gap" for i in qc_gap["issues"])
