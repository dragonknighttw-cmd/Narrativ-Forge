import pytest

pytestmark = pytest.mark.unit

from app.services.phase_61_68 import (
    AuditAction,
    AuditEvent,
    AutoscalePolicy,
    LocalizationQA,
    MonetizationLedger,
    PerformanceBudget,
    ProvenanceRecord,
    ProviderCapability,
    SLOObservation,
    SLOSeverity,
    validate_operating_inputs,
)


def test_performance_and_autoscaling_contracts():
    budget = PerformanceBudget("/render", 800, 0.01, 0.25)
    policy = AutoscalePolicy(1, 8, 10, 2)
    assert budget.valid()
    assert policy.valid()
    assert policy.desired_workers(25, 3) == 5
    assert policy.desired_workers(2, 3) == 1


def test_provenance_and_audit_are_immutable_inputs():
    provenance = ProvenanceRecord("asset-1", ("source-1",), "provider", "v2", "sha256", "ledger-1")
    audit = AuditEvent("owner", "series-1", AuditAction.APPROVE, "episode-1", "event-1")
    assert provenance.valid()
    assert audit.valid()


def test_provider_capability_respects_health_and_circuit_breaker():
    provider = ProviderCapability("provider-a", "v1", ("transcribe", "render"), True)
    assert provider.available("transcribe")
    assert not ProviderCapability("provider-a", "v1", ("transcribe",), False).available("transcribe")
    assert not ProviderCapability("provider-a", "v1", ("transcribe",), True, True).available("transcribe")


def test_localization_and_monetization_contracts():
    qa = LocalizationQA("my", "glossary-v2", 0.98, 0.02, 3)
    ledger = MonetizationLedger("tenant", "pro", 1000, 400, 50, "billing-1")
    assert qa.valid()
    assert ledger.valid()
    assert ledger.remaining() == 650


def test_slo_severity_consumes_error_budget():
    assert SLOObservation("api", 0.999, 300, 0.5).severity(0.99, 500) == SLOSeverity.OK
    assert SLOObservation("api", 0.98, 300, 0.5).severity(0.99, 500) == SLOSeverity.FREEZE
    assert SLOObservation("api", 0.98, 300, 0,).severity(0.99, 500) == SLOSeverity.INCIDENT


def test_all_post_60_contracts_validate_together():
    errors = validate_operating_inputs(
        PerformanceBudget("/api", 500, 0.01, 0.1),
        AutoscalePolicy(1, 4, 10, 1),
        ProvenanceRecord("a", ("source",), "p", "v1", "hash", "ref"),
        AuditEvent("actor", "scope", AuditAction.UPDATE, "target", "event"),
        ProviderCapability("p", "v1", ("render",), True),
        LocalizationQA("my", "v1", 0.95, 0.01, 0),
        MonetizationLedger("tenant", "free", 100, 10, 0, "idem"),
        SLOObservation("api", 0.999, 100, 0.5),
    )
    assert errors == []
