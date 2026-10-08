from datetime import datetime, timedelta, timezone

import pytest

from app.services.operating_maturity import (
    CostBand, CostPolicy, EvaluationDataset, ModelChange, ModelVersion,
    OperatingDrill, QueueJob, QueuePriority, RegionPolicy, ReleaseManifest,
    RetentionClass, RestorePoint, SchedulingPolicy, select_restore_point,
    validate_evaluation_dataset, validate_region_policy, validate_release_manifest,
)


@pytest.mark.unit
def test_release_manifest_requires_rollback_and_migration_window():
    assert validate_release_manifest(ReleaseManifest("1.0.0", "abc", "expand-contract", "previous")) == []
    assert validate_release_manifest(ReleaseManifest("", "abc", "window", "previous"))


@pytest.mark.unit
def test_cost_policy_bands_are_deterministic():
    policy = CostPolicy(10, 20)
    assert policy.classify(5) == CostBand.NORMAL
    assert policy.classify(10) == CostBand.WARNING
    assert policy.classify(20) == CostBand.CRITICAL


@pytest.mark.unit
def test_region_policy_requires_preferred_region():
    assert validate_region_policy(RegionPolicy("us", ("us", "eu"), True)) == []
    assert "preferred_region_not_allowed" in validate_region_policy(RegionPolicy("ap", ("us",), True))


@pytest.mark.unit
def test_queue_admission_respects_capacity():
    policy = SchedulingPolicy(2, 10)
    job = QueueJob("j", "t", QueuePriority.INTERACTIVE, 4, datetime.now(timezone.utc))
    assert policy.admit(job, 6)
    assert not policy.admit(job, 7)


@pytest.mark.unit
def test_restore_point_selection_is_latest():
    now = datetime.now(timezone.utc)
    points = [
        RestorePoint("old", now - timedelta(hours=2), "a", "backup"),
        RestorePoint("new", now - timedelta(hours=1), "b", "backup"),
    ]
    assert select_restore_point(points).key == "new"


@pytest.mark.unit
def test_evaluation_dataset_requires_anonymization():
    dataset = EvaluationDataset("burmese", "v1", "curated-owner-approved", True, 92)
    assert validate_evaluation_dataset(dataset) == []
    dataset = EvaluationDataset("burmese", "v1", "curated", False, 92)
    assert "anonymization_required" in validate_evaluation_dataset(dataset)


@pytest.mark.unit
def test_model_change_blocks_quality_regression():
    old = ModelVersion("p", "m", "1", 90, 80)
    candidate = ModelVersion("p", "m", "2", 88, 70)
    assert ModelChange(old, candidate, 89).regression(85)


@pytest.mark.unit
def test_operating_drill_is_overdue_without_evidence():
    drill = OperatingDrill("DR", "owner", datetime.now(timezone.utc) - timedelta(minutes=1))
    assert drill.overdue
