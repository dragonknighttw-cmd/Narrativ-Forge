"""Code-only foundations for the Phase 77-84 operating backlog."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence


@dataclass(frozen=True)
class CapacityForecast:
    tenant: str
    projected_units: int
    quota_units: int
    reserved_units: int = 0
    horizon_days: int = 1

    def valid(self) -> bool:
        return bool(self.tenant.strip()) and self.projected_units >= 0 and self.quota_units >= 0 and self.reserved_units >= 0 and self.horizon_days > 0

    def headroom(self) -> int:
        return self.quota_units - self.reserved_units - self.projected_units

    def within_quota(self) -> bool:
        return self.valid() and self.headroom() >= 0


@dataclass(frozen=True)
class ApiVersionPolicy:
    resource: str
    current: int
    minimum_supported: int
    sunset_version: int | None = None

    def valid(self) -> bool:
        return bool(self.resource.strip()) and 1 <= self.minimum_supported <= self.current and (self.sunset_version is None or self.sunset_version >= self.minimum_supported)

    def supported(self, version: int) -> bool:
        return self.valid() and self.minimum_supported <= version <= self.current and (self.sunset_version is None or version < self.sunset_version)


@dataclass(frozen=True)
class MigrationRetirement:
    migration_id: str
    replacement_id: str
    references_cleared: bool
    rollback_window_closed: bool
    data_cleanup_complete: bool

    def ready(self) -> bool:
        return bool(self.migration_id.strip() and self.replacement_id.strip() and self.references_cleared and self.rollback_window_closed and self.data_cleanup_complete)


@dataclass(frozen=True)
class TenantExportManifest:
    tenant: str
    schema_version: str
    object_refs: tuple[str, ...]
    checksum: str
    encrypted: bool

    @property
    def export_key(self) -> str:
        return sha256("|".join((self.tenant, self.schema_version, self.checksum, *sorted(self.object_refs))).encode()).hexdigest()

    def valid(self) -> bool:
        return bool(self.tenant.strip() and self.schema_version.strip() and self.object_refs and self.checksum.strip() and self.encrypted)


@dataclass(frozen=True)
class IncidentCommunication:
    incident_id: str
    audience: str
    status: str
    message_ref: str
    acknowledged: bool = False

    def valid(self) -> bool:
        return bool(self.incident_id.strip() and self.audience.strip() and self.status in {"investigating", "identified", "monitoring", "resolved"} and self.message_ref.strip())


@dataclass(frozen=True)
class SupportSla:
    priority: str
    response_minutes: int
    resolution_minutes: int
    escalation_after_minutes: int

    def valid(self) -> bool:
        return self.priority in {"critical", "high", "normal", "low"} and 0 < self.response_minutes <= self.resolution_minutes and self.response_minutes <= self.escalation_after_minutes


@dataclass(frozen=True)
class SettlementRecord:
    provider: str
    settlement_id: str
    gross_units: int
    fees_units: int
    net_units: int
    idempotency_key: str

    def valid(self) -> bool:
        return bool(self.provider.strip() and self.settlement_id.strip() and self.idempotency_key.strip() and self.gross_units >= 0 and self.fees_units >= 0 and self.net_units == self.gross_units - self.fees_units)


@dataclass(frozen=True)
class GovernanceOwner:
    area: str
    owner: str
    backup: str
    evidence_refs: tuple[str, ...] = ()

    def valid(self) -> bool:
        return bool(self.area.strip() and self.owner.strip() and self.backup.strip())

    def evidenced(self) -> bool:
        return self.valid() and bool(self.evidence_refs)


def validate_final_governance(
    capacity: CapacityForecast,
    api: ApiVersionPolicy,
    retirement: MigrationRetirement,
    export: TenantExportManifest,
    incident: IncidentCommunication,
    sla: SupportSla,
    settlement: SettlementRecord,
    owners: Sequence[GovernanceOwner],
) -> list[str]:
    errors: list[str] = []
    if not capacity.within_quota(): errors.append("capacity_forecast_exceeds_quota")
    if not api.valid(): errors.append("api_version_policy_invalid")
    if not retirement.ready(): errors.append("migration_retirement_unready")
    if not export.valid(): errors.append("tenant_export_invalid")
    if not incident.valid(): errors.append("incident_communication_invalid")
    if not sla.valid(): errors.append("support_sla_invalid")
    if not settlement.valid(): errors.append("settlement_invalid")
    if not owners or not all(o.evidenced() for o in owners): errors.append("governance_evidence_incomplete")
    return errors
