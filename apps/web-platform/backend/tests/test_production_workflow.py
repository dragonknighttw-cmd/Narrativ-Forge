import pytest

from app.services.phase_61_68 import (
    AutoscalePolicy,
    BillingMeter,
    EnterprisePermission,
    IncidentPolicy,
    LocaleQualityRecord,
    PerformanceBudget,
    ProvenanceRecord,
    ProviderCapability,
    SLOBudget,
    adapter_capabilities,
)

pytestmark = pytest.mark.unit


def test_performance_budget_and_autoscaling_are_deterministic():
    assert PerformanceBudget("render", 10, 1).check(9.9, 0.5)
    policy = AutoscalePolicy(1, 5, 10, 2)
    assert policy.desired_workers(12, 2) == 3
    assert policy.desired_workers(0, 3) == 2


def test_provenance_is_stable_for_same_lineage():
    record = ProvenanceRecord("a", ("p1", "p2"), "model", "v1", "provider", "hash")
    assert record.lineage_key == ProvenanceRecord("a", ("p1", "p2"), "model", "v1", "provider", "hash").lineage_key


def test_enterprise_permission_and_provider_capabilities():
    assert EnterprisePermission("editor", "project", "write", True).allowed
    records = [
        ProviderCapability("a", "translate", "v1", True),
        ProviderCapability("a", "render", "v2", False),
        ProviderCapability("b", "render", "v1", True),
    ]
    assert adapter_capabilities(records) == {"a": {"translate"}, "b": {"render"}}


def test_localization_and_billing_validation():
    assert LocaleQualityRecord("my", "g1", "h", 0.02).acceptable(0.05)
    with pytest.raises(ValueError):
        BillingMeter("tenant", -1, "key").validate()


def test_slo_and_incident_policy():
    assert SLOBudget("api", 99.9, 500, 0.1).valid()
    policy = IncidentPolicy(thresholds={"burn": 5, "critical_error": 1})
    assert policy.action_for("burn", 5) == "freeze"
    assert policy.action_for("critical_error", 1) == "rollback"
