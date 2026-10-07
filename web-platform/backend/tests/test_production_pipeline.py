import pytest
from datetime import datetime, timedelta, timezone

from app.services.production_pipeline import (
    ABOutcome,
    TrendSignal,
    build_cross_platform_export_plan,
    build_series_trailer_plan,
    build_translation_request,
    rank_ab_outcomes,
    rank_trend_signals,
    score_ab_outcome,
    validate_cross_platform_export_plan,
    validate_translation_result,
)


pytestmark = pytest.mark.unit


def test_cross_platform_plan_is_bounded_and_valid():
    plan = build_cross_platform_export_plan(240)
    assert plan["youtube_shorts"]["requires_trim"] is True
    assert plan["youtube_shorts"]["max_duration_seconds"] == 180
    assert validate_cross_platform_export_plan(plan) == []


def test_trend_ranking_drops_expired_signals():
    now = datetime.now(timezone.utc)
    signals = [
        TrendSignal("fresh", 10, "test", now, now + timedelta(hours=1)),
        TrendSignal("expired", 99, "test", now, now - timedelta(seconds=1)),
    ]
    assert [item.topic for item in rank_trend_signals(signals, now=now)] == ["fresh"]


def test_ab_outcomes_rank_by_normalized_engagement():
    strong = ABOutcome("a", impressions=100, views=80, completions=60, shares=10)
    weak = ABOutcome("b", impressions=100, views=50, completions=20, shares=1)
    assert score_ab_outcome(strong) > score_ab_outcome(weak)
    assert [item.variant_key for item in rank_ab_outcomes([weak, strong])] == ["a", "b"]


def test_series_trailer_plan_respects_duration_budget():
    scenes = [
        {"scene_number": 2, "purpose": "body", "dialogue": "Body", "duration_seconds": 20},
        {"scene_number": 1, "purpose": "hook", "dialogue": "Hook", "duration_seconds": 20},
    ]
    plan = build_series_trailer_plan(scenes, max_duration_seconds=25)
    assert plan[0].scene_number == 1
    assert sum(item.duration_seconds for item in plan) <= 25


def test_translation_request_is_burmese_first_and_preserves_lines():
    request = build_translation_request("မင်္ဂလာပါ\nနေကောင်းလား", "en")
    assert request.source_language == "my"
    assert request.target_language == "en"
    assert validate_translation_result(request, "Hello\nHow are you?") == "Hello\nHow are you?"
