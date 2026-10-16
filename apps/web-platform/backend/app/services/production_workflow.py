"""Code-only foundations for the Phase 61-68 continuation queue.

These contracts are deliberately provider-neutral. They can be wired to live
telemetry, billing, provider and enterprise systems later without pretending
that a live acceptance gate has passed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Mapping, Sequence


@dataclass(frozen=True)
class PerformanceBudget:
    operation: str
    max_seconds: float
    max_cost_usd: float

    def check(self, elapsed_seconds: float, cost_usd: float) -> bool:
        return elapsed_seconds <= self.max_seconds and cost_usd <= self.max_cost_usd


@dataclass(frozen=True)
class AutoscalePolicy:
    min_workers: int
    max_workers: int
    scale_up_queue: int
    scale_down_queue: int

    def desired_workers(self, queue_depth: int, current: int) -> int:
        if queue_depth >= self.scale_up_queue:
            return min(self.max_workers, max(current + 1, self.min_workers))
        if queue_depth <= self.scale_down_queue:
            return max(self.min_workers, current - 1)
        return max(self.min_workers, min(self.max_workers, current))


@dataclass(frozen=True)
class ProvenanceRecord:
    asset_id: str
    parent_ids: tuple[str, ...]
    model: str
    model_version: str
    provider: str
    source_hash: str

    @property
    def lineage_key(self) -> str:
        payload = "|".join((self.asset_id, *self.parent_ids, self.model, self.model_version, self.provider, self.source_hash))
        return sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class EnterprisePermission:
    role: str
    resource: str
    action: str
    allowed: bool


@dataclass(frozen=True)
class ProviderCapability:
    provider: str
    capability: str
    version: str
    healthy: bool


@dataclass(frozen=True)
class LocaleQualityRecord:
    locale: str
    glossary_version: str
    source_hash: str
    subtitle_error_rate: float

    def acceptable(self, max_error_rate: float) -> bool:
        return self.subtitle_error_rate <= max_error_rate


@dataclass(frozen=True)
class BillingMeter:
    tenant_key: str
    units: int
    idempotency_key: str

    def validate(self) -> None:
        if self.units < 0:
            raise ValueError("units must be non-negative")
        if not self.tenant_key or not self.idempotency_key:
            raise ValueError("tenant_key and idempotency_key are required")


@dataclass(frozen=True)
class SLOBudget:
    service: str
    availability_target: float
    latency_ms_p95: int
    error_budget_percent: float

    def valid(self) -> bool:
        return (
            0 < self.availability_target <= 100
            and self.latency_ms_p95 > 0
            and 0 <= self.error_budget_percent <= 100
        )


@dataclass
class IncidentPolicy:
    freeze_on_burn: bool = True
    rollback_on_critical: bool = True
    thresholds: Mapping[str, float] = field(default_factory=dict)

    def action_for(self, signal: str, value: float) -> str:
        threshold = self.thresholds.get(signal)
        if threshold is None:
            return "observe"
        if value >= threshold:
            if signal == "critical_error" and self.rollback_on_critical:
                return "rollback"
            if self.freeze_on_burn:
                return "freeze"
        return "observe"


def adapter_capabilities(records: Sequence[ProviderCapability]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for record in records:
        if record.healthy:
            result.setdefault(record.provider, set()).add(record.capability)
    return result
