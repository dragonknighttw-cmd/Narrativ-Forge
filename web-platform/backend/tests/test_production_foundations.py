import pytest

pytestmark = pytest.mark.unit

from datetime import datetime, timezone

import pytest

from app.services.auto_mode import normalize_content_plan
from app.services.ai_adapter import ContentPlan
from app.services.hook_engineering import generate_hook_candidates
from app.services.provider_fallback import ProviderNonRetryableError, run_with_fallback
from app.services.production_pipeline import (
    build_cross_platform_export_plan,
    build_production_metadata,
    build_thumbnail_plan,
    plan_batch,
    assess_production_readiness,
)
from app.services.storage_lifecycle import can_delete_asset, classify_storage_usage, StorageThresholds


def test_auto_plan_is_normalized_to_target_duration():
    plan = ContentPlan(
        hook="hook",
        script="script",
        scenes=[{"scene_number": 1, "purpose": "hook", "description": "h", "dialogue": "h", "duration_seconds": 5}],
    )
    normalized = normalize_content_plan(plan, 180)
    assert sum(scene["duration_seconds"] for scene in normalized.scenes) == 180
    assert len(normalized.scenes) >= 4


def test_hook_engineering_covers_all_eight_hook_families():
    candidates = generate_hook_candidates("မြန်မာအကြောင်းအရာ")
    assert len(candidates) == 8
    assert {item.hook_type for item in candidates} == {
        "question", "curiosity_gap", "bold_claim", "story",
        "problem_solution", "number", "contrast", "challenge",
    }


def test_provider_fallback_uses_next_provider_on_retryable_failure():
    calls = []
    def broken():
        calls.append("primary")
        raise TimeoutError("temporary")
    def backup():
        calls.append("backup")
        return "ok"

    value, provider, attempts = run_with_fallback([("primary", broken), ("backup", backup)])
    assert value == "ok"
    assert provider == "backup"
    assert calls == ["primary", "backup"]
    assert [item.ok for item in attempts] == [False, True]


def test_provider_fallback_rejects_non_retryable_error():
    def invalid():
        raise ValueError("invalid request")
    with pytest.raises(ProviderNonRetryableError):
        run_with_fallback([("primary", invalid)])


def test_metadata_thumbnail_and_platform_export_foundations():
    metadata = build_production_metadata("ခေါင်းစဉ်", "အကြောင်းအရာ", "Hook", ["မြန်မာ", "shorts"])
    assert metadata.thumbnail_text
    assert metadata.sound_plan["commercial_safe_required"] is True
    assert metadata.platform_exports["master"]["resolution"] == "1080x1920"
    assert len(metadata.hashtags) == 2
    assert build_thumbnail_plan("Title", "A " * 40)["aspect_ratio"] == "9:16"
    assert build_cross_platform_export_plan(180)["youtube_shorts"]["max_duration_seconds"] == 180


def test_batch_calendar_is_deterministic():
    start = datetime(2026, 10, 7, 12, tzinfo=timezone.utc)
    rows = plan_batch([{"key": "ep1"}, {"key": "ep2"}], start_at=start, interval_minutes=30)
    assert rows[0].scheduled_at == start
    assert rows[1].scheduled_at > rows[0].scheduled_at
    assert rows[0].platform == "youtube_shorts"


def test_storage_cleanup_protects_final_approved_and_only_copy():
    assert can_delete_asset(is_final=False, is_approved=False, is_only_copy=False, retention_expired=True)
    assert not can_delete_asset(is_final=True, is_approved=False, is_only_copy=False, retention_expired=True)
    assert not can_delete_asset(is_final=False, is_approved=True, is_only_copy=False, retention_expired=True)
    assert classify_storage_usage(80, 100).state() == "warning"
    assert classify_storage_usage(95, 100).state() == "emergency"


def test_production_readiness_blocks_continuity_issues():
    ready = assess_production_readiness(
        script=" ".join(["script"] * 100),
        scene_durations=[30, 30, 30, 30, 30, 30],
        target_seconds=180,
    )
    assert ready.ready_for_review is True

    blocked = assess_production_readiness(
        script=" ".join(["script"] * 100),
        scene_durations=[30, 30, 30, 30, 30, 30],
        target_seconds=180,
        continuity_issues=["missing recurring element"],
    )
    assert blocked.ready_for_review is False


def test_storage_thresholds_must_be_ordered():
    with pytest.raises(ValueError):
        StorageThresholds(warning=0.90, critical=0.80, emergency=0.95)
    with pytest.raises(ValueError):
        StorageThresholds(warning=-0.1, critical=0.80, emergency=0.95)


def test_provider_fallback_records_all_failures():
    def first():
        raise TimeoutError("first timeout")

    def second():
        raise RuntimeError("service unavailable")

    with pytest.raises(RuntimeError, match="All providers failed"):
        run_with_fallback([("primary", first), ("backup", second)])


def test_provider_fallback_does_not_call_backup_for_invalid_request():
    calls = []

    def invalid():
        calls.append("primary")
        raise ValueError("invalid request")

    def backup():
        calls.append("backup")
        return "unexpected"

    with pytest.raises(ProviderNonRetryableError):
        run_with_fallback([("primary", invalid), ("backup", backup)])
    assert calls == ["primary"]
