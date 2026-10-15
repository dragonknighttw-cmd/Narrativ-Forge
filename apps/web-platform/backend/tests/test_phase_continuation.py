import pytest

pytestmark = pytest.mark.unit

from datetime import datetime, timezone, timedelta

from app.services.phase_continuation import (
    CachedTrend, CollaborationLock, Experiment, ExperimentVariant,
    ExportManifest, LaunchEvidence, NLEManifest, ProviderQualityScore, UsageReservation,
    choose_experiment_winner, launch_summary, rank_providers,
    validate_experiment, validate_export_manifest, validate_lock,
    validate_nle_manifest, validate_usage_reservation,
)


@pytest.mark.unit
def test_export_manifest_is_deterministic_and_validates():
    manifest = ExportManifest("youtube", "ep-1", "Title", "Caption", ("#a",))
    assert manifest.key() == manifest.key()
    assert validate_export_manifest(manifest) == []


@pytest.mark.unit
def test_trend_cache_expiry():
    now = datetime.now(timezone.utc)
    fresh = CachedTrend("provider", "k", ("x",), now, 60)
    assert fresh.fresh(now=now + timedelta(seconds=30))
    assert not fresh.fresh(now=now + timedelta(seconds=61))


@pytest.mark.unit
def test_experiment_requires_safe_weights_and_minimum_samples():
    experiment = Experiment("exp", (ExperimentVariant("a", .5), ExperimentVariant("b", .5)), 10)
    assert validate_experiment(experiment) == []
    assert choose_experiment_winner({"a": .9, "b": .8}, sample_count=10, min_samples=10) == "a"
    assert choose_experiment_winner({"a": .9}, sample_count=9, min_samples=10) is None


@pytest.mark.unit
def test_provider_ranking_is_deterministic():
    scores = [ProviderQualityScore("slow", 90, 500, 5), ProviderQualityScore("fast", 85, 100, 1)]
    assert rank_providers(scores)[0].provider == "fast"


@pytest.mark.unit
def test_nle_manifest_rejects_overlap():
    manifest = NLEManifest("fcpxml", 30, 10, ({"start": 0, "end": 5}, {"start": 4, "end": 8}))
    assert "clip_overlap" in validate_nle_manifest(manifest)


@pytest.mark.unit
def test_optimistic_lock_and_usage_reservation():
    lock = CollaborationLock("episode-1", "user-1", 3)
    validate_lock(3, lock)
    with pytest.raises(ValueError, match="optimistic_lock_conflict"):
        validate_lock(4, lock)
    assert validate_usage_reservation(UsageReservation("tenant", "gpu_seconds", 10, "id-1")) == []


@pytest.mark.unit
def test_launch_summary_blocks_unverified_gates():
    result = launch_summary([
        LaunchEvidence("ci", "verified"),
        LaunchEvidence("stripe", "pending"),
    ])
    assert result == {"ready": False, "blocked_gates": ["stripe"], "count": 2}


@pytest.mark.unit
def test_export_manifest_key_changes_when_identity_changes():
    first = ExportManifest("youtube", "ep-1", "Title", "Caption", ("#a",))
    second = ExportManifest("youtube", "ep-2", "Title", "Caption", ("#a",))
    assert first.key() != second.key()


@pytest.mark.unit
def test_experiment_rejects_duplicate_variant_keys():
    experiment = Experiment("exp", (ExperimentVariant("a", .5), ExperimentVariant("a", .5)), 10)
    assert validate_experiment(experiment) == ["duplicate_variant_key"]


@pytest.mark.unit
def test_nle_manifest_accepts_adjacent_clips():
    manifest = NLEManifest("edl", 24, 8, ({"start": 0, "end": 4}, {"start": 4, "end": 8}))
    assert validate_nle_manifest(manifest) == []


@pytest.mark.unit
def test_launch_summary_treats_waived_as_unblocking():
    assert launch_summary([
        LaunchEvidence("security", "waived", ("owner-approval",)),
    ])["ready"]

