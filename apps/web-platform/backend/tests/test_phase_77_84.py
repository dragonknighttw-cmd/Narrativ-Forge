import pytest

pytestmark = pytest.mark.unit

from app.services.phase_77_84 import (
    ApiVersionPolicy, CapacityForecast, GovernanceOwner, IncidentCommunication,
    MigrationRetirement, SettlementRecord, SupportSla, TenantExportManifest,
    validate_final_governance,
)


def test_capacity_forecast_respects_reserved_quota():
    ok = CapacityForecast("tenant-a", 70, 100, 20, 7)
    bad = CapacityForecast("tenant-a", 81, 100, 20, 7)
    assert ok.within_quota()
    assert ok.headroom() == 10
    assert not bad.within_quota()


def test_api_version_policy_and_sunset():
    policy = ApiVersionPolicy("episodes", 3, 1, 3)
    assert policy.valid()
    assert policy.supported(1)
    assert policy.supported(2)
    assert not policy.supported(3)


def test_migration_retirement_requires_all_safety_conditions():
    assert MigrationRetirement("m001", "m002", True, True, True).ready()
    assert not MigrationRetirement("m001", "m002", True, False, True).ready()


def test_tenant_export_key_is_deterministic_and_identity_bound():
    a = TenantExportManifest("tenant-a", "v1", ("b", "a"), "checksum", True)
    b = TenantExportManifest("tenant-a", "v1", ("a", "b"), "checksum", True)
    c = TenantExportManifest("tenant-b", "v1", ("a", "b"), "checksum", True)
    assert a.valid()
    assert a.export_key == b.export_key
    assert a.export_key != c.export_key


def test_incident_communication_and_sla():
    assert IncidentCommunication("inc-1", "customers", "monitoring", "status-42").valid()
    assert not IncidentCommunication("inc-1", "customers", "draft", "status-42").valid()
    assert SupportSla("critical", 15, 120, 30).valid()
    assert not SupportSla("critical", 0, 120, 30).valid()


def test_settlement_is_math_and_idempotency_safe():
    assert SettlementRecord("provider-x", "set-1", 1000, 75, 925, "evt-1").valid()
    assert not SettlementRecord("provider-x", "set-1", 1000, 75, 900, "evt-1").valid()


def test_final_governance_blocks_incomplete_evidence():
    common = dict(
        capacity=CapacityForecast("tenant-a", 20, 100, 10, 7),
        api=ApiVersionPolicy("episodes", 2, 1),
        retirement=MigrationRetirement("m1", "m2", True, True, True),
        export=TenantExportManifest("tenant-a", "v1", ("asset-1",), "sha", True),
        incident=IncidentCommunication("inc-1", "customers", "resolved", "status-1"),
        sla=SupportSla("normal", 60, 1440, 120),
        settlement=SettlementRecord("provider", "set-1", 100, 5, 95, "evt-1"),
    )
    assert validate_final_governance(**common, owners=[GovernanceOwner("release", "owner", "backup", ("ev-1",))]) == []
    assert "governance_evidence_incomplete" in validate_final_governance(**common, owners=[GovernanceOwner("release", "owner", "backup")])
