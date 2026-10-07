import pytest
from datetime import datetime, timezone, timedelta

from app.services.production_scale import (
    AlertRule,
    ComplianceCheck,
    DisasterRecoveryTarget,
    ExperimentOutcome,
    PlatformMetadata,
    TimelineClip,
    TrendCache,
    TrendRateLimitError,
    build_edl,
    build_nle_manifest,
    build_publish_attempt_key,
    compliance_gate,
    evaluate_alert,
    lifecycle_action,
    rank_ai_providers,
    select_experiment_winner,
    validate_dr_target,
    validate_platform_metadata,
    validate_timeline,
)
from app.services.future_foundations import (
    Dependency,
    LaunchGate,
    QuotaBudget,
    ReviewLearningEvent,
    ReviewLearningModel,
    UsageQuota,
    affected_by_change,
    build_demo_seed,
    build_regeneration_plan,
    enforce_usage_quota,
    evaluate_launch_gate,
    plan_quota_aware_batch,
)


pytestmark = pytest.mark.unit


def test_publish_contract_validates_and_is_idempotent_by_key():
    metadata = PlatformMetadata("youtube_shorts", "Episode 1")
    assert validate_platform_metadata(metadata) == []
    assert build_publish_attempt_key("ep-1", "youtube_shorts") == build_publish_attempt_key("ep-1", "youtube_shorts")
    assert build_publish_attempt_key("ep-1", "youtube_shorts") != build_publish_attempt_key("ep-2", "youtube_shorts")


def test_trend_cache_and_expiry_contract():
    cache = TrendCache(ttl_seconds=10)
    cache.put("x", [], now=0)
    assert cache.get("x", now=1) is not None
    assert cache.get("x", now=11) is None


def test_experiment_winner_requires_guardrails():
    assert select_experiment_winner(
        [ExperimentOutcome("a", 1000, 150), ExperimentOutcome("b", 1000, 100)],
        min_impressions=100,
    ) == "a"
    assert select_experiment_winner(
        [ExperimentOutcome("a", 100, 51), ExperimentOutcome("b", 100, 50)],
        min_impressions=100,
        min_lift=0.10,
    ) is None


def test_ai_provider_ranking_filters_capability():
    from app.services.production_scale import ProviderEvaluation
    ranked = rank_ai_providers([
        ProviderEvaluation("a", "script", {"quality": 90, "latency": 80, "cost": 80}, 10),
        ProviderEvaluation("b", "script", {"quality": 80, "latency": 90, "cost": 90}, 10),
        ProviderEvaluation("x", "video", {"quality": 99}, 10),
    ], capability="script")
    assert ranked[0].provider == "a"


def test_nle_timeline_rejects_overlap_and_builds_edl():
    clips = [TimelineClip("a", 0, 2), TimelineClip("b", 2, 4)]
    assert validate_timeline(clips) == []
    assert "FROM CLIP NAME: a" in build_edl(clips)
    assert build_nle_manifest("ep-1", clips)["format"] == "fcpxml"
    assert validate_timeline([TimelineClip("a", 0, 2), TimelineClip("b", 1, 3)])


def test_storage_lifecycle_never_deletes_approved_or_referenced_output():
    from app.services.production_scale import LifecyclePolicy
    policy = LifecyclePolicy(delete_after_days=30)
    assert lifecycle_action(100, policy, is_approved_final=True, is_referenced=False) == "retain"
    assert lifecycle_action(100, policy, is_approved_final=False, is_referenced=True) == "retain"
    assert lifecycle_action(100, policy, is_approved_final=False, is_referenced=False) == "delete"


def test_dr_alert_and_compliance_contracts():
    assert validate_dr_target(DisasterRecoveryTarget(15, 60)) == []
    assert evaluate_alert(AlertRule("queue", "queue_depth", 10), 10)
    assert compliance_gate([ComplianceCheck("a", True), ComplianceCheck("b", False)]) == (False, ["b"])


def test_dependency_regeneration_invalidates_only_dependents():
    deps = [Dependency("script", "scene"), Dependency("scene", "subtitle"), Dependency("unrelated", "other")]
    assert affected_by_change("script", deps) == {"script", "scene", "subtitle"}
    plan = build_regeneration_plan("script", deps, ["script", "scene", "subtitle", "other"])
    assert plan.invalidated_keys == ("scene", "script", "subtitle")
    assert plan.preserved_keys == ("other",)


def test_quota_batch_and_enforcement():
    jobs = plan_quota_aware_batch(
        [
            __import__("app.services.future_foundations", fromlist=["BatchJob"]).BatchJob("a", 4, 1),
            __import__("app.services.future_foundations", fromlist=["BatchJob"]).BatchJob("b", 8, 2),
        ],
        [QuotaBudget("provider", 10, 0)],
    )
    assert [job.key for job in jobs] == ["a"]
    enforce_usage_quota(UsageQuota("compute", 10, 9), 1)
    with pytest.raises(PermissionError):
        enforce_usage_quota(UsageQuota("compute", 10, 10), 1)


def test_review_learning_demo_and_launch_gate():
    model = ReviewLearningModel()
    model.ingest(ReviewLearningEvent("reject", ("timing", "timing")))
    assert model.top_issues(1) == [("timing", 2)]
    seed = build_demo_seed("series", 2)
    assert len(seed.episode_keys) == 2
    assert evaluate_launch_gate([LaunchGate("code", True), LaunchGate("worker", False)]) == (False, ["worker"])
