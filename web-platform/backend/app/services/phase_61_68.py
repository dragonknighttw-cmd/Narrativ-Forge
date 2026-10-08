"""Code-only contracts for the post-60 operating backlog.

These models make performance, autoscaling, provenance, enterprise audit,
provider adapters, localization QA, monetization and SLO operations
testable without requiring live credentials or external services.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SLOSeverity(str, Enum):
    WARNING = "warning"
    FREEZE = "freeze"
    INCIDENT = "incident"


@dataclass(frozen=True)
class PerformanceBudget:
    route: str
    p95_ms: float
    error_rate: float
    cost_per_job: float

    def valid(self) -> bool:
        return bool(self.route.strip() and self.p95_ms > 0 and 0 <= self.error_rate <= 1 and self.cost_per_job >= 0)


@dataclass(frozen=True)
class AutoscalePolicy:
    min_workers: int
    max_workers: int
    queue_target: int
    scale_step: int

    def valid(self) -> bool:
        return 1 <= self.min_workers <= self.max_workers and self.queue_target > 0 and self.scale_step > 0

    def desired_workers(self, queue_depth: int, current: int) -> int:
        if not self.valid():
            raise ValueError("invalid autoscale policy")
        if queue_depth <= self.queue_target:
            return max(self.min_workers, current - self.scale_step)
        return min(self.max_workers, current + self.scale_step)


@dataclass(frozen=True)
class ProvenanceRecord:
    asset_id: str
    parent_refs: tuple[str, ...]
    model_provider: str
    model_version: str
    source_hash: str
    immutable_ref: str

    def valid(self) -> bool:
        return bool(
            self.asset_id.strip()
            and self.parent_refs
            and self.model_provider.strip()
            and self.model_version.strip()
            and self.source_hash.strip()
            and self.immutable_ref.strip()
        )


class AuditAction(str, Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"


@dataclass(frozen=True)
class AuditEvent:
    actor: str
    scope: str
    action: AuditAction
    target: str
    event_id: str

    def valid(self) -> bool:
        return all(value.strip() for value in (self.actor, self.scope, self.target, self.event_id))


@dataclass(frozen=True)
class ProviderCapability:
    provider: str
    version: str
    capabilities: tuple[str, ...]
    healthy: bool
    circuit_open: bool = False

    def available(self, capability: str) -> bool:
        return self.healthy and not self.circuit_open and capability in self.capabilities


@dataclass(frozen=True)
class LocalizationQA:
    locale: str
    glossary_version: str
    terminology_score: float
    subtitle_error_rate: float
    correction_count: int

    def valid(self) -> bool:
        return bool(
            self.locale.strip()
            and self.glossary_version.strip()
            and 0 <= self.terminology_score <= 1
            and 0 <= self.subtitle_error_rate <= 1
            and self.correction_count >= 0
        )


@dataclass(frozen=True)
class MonetizationLedger:
    tenant_key: str
    entitlement: str
    quota_units: int
    used_units: int
    credit_units: int
    idempotency_key: str

    def remaining(self) -> int:
        return self.quota_units + self.credit_units - self.used_units

    def valid(self) -> bool:
        return bool(self.tenant_key.strip() and self.entitlement.strip() and self.idempotency_key.strip()) and min(
            self.quota_units, self.used_units, self.credit_units
        ) >= 0


@dataclass(frozen=True)
class SLOObservation:
    service: str
    availability: float
    p95_ms: float
    error_budget_remaining: float

    def severity(self, availability_target: float, p95_target_ms: float) -> SLOSeverity:
        if self.availability < availability_target or self.p95_ms > p95_target_ms:
            return SLOSeverity.INCIDENT if self.error_budget_remaining <= 0 else SLOSeverity.FREEZE
        if self.error_budget_remaining < 0.1:
            return SLOSeverity.WARNING
        return SLOSeverity.WARNING if self.error_budget_remaining < 0.25 else SLOSeverity.WARNING


def validate_operating_inputs(
    performance: PerformanceBudget,
    autoscale: AutoscalePolicy,
    provenance: ProvenanceRecord,
    audit: AuditEvent,
    provider: ProviderCapability,
    localization: LocalizationQA,
    billing: MonetizationLedger,
    slo: SLOObservation,
) -> list[str]:
    errors: list[str] = []
    if not performance.valid(): errors.append("performance_invalid")
    if not autoscale.valid(): errors.append("autoscale_invalid")
    if not provenance.valid(): errors.append("provenance_invalid")
    if not audit.valid(): errors.append("audit_invalid")
    if not provider.provider.strip() or not provider.version.strip(): errors.append("provider_invalid")
    if not localization.valid(): errors.append("localization_invalid")
    if not billing.valid(): errors.append("billing_invalid")
    if not slo.service.strip() or not 0 <= slo.availability <= 1 or slo.p95_ms < 0: errors.append("slo_invalid")
    return errors
