from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable


@dataclass(frozen=True)
class ReleaseManifest:
    version: str
    commit_sha: str
    migration_window: str
    rollback_ref: str

    def valid(self) -> bool:
        return all((self.version.strip(), self.commit_sha.strip(), self.migration_window.strip(), self.rollback_ref.strip()))


class CostBand(str, Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class CostObservation:
    tenant_key: str
    provider: str
    units: float
    estimated_cost: float
    observed_at: datetime


@dataclass(frozen=True)
class CostPolicy:
    warning_cost: float
    critical_cost: float

    def classify(self, cost: float) -> CostBand:
        if cost >= self.critical_cost:
            return CostBand.CRITICAL
        if cost >= self.warning_cost:
            return CostBand.WARNING
        return CostBand.NORMAL


@dataclass(frozen=True)
class RetentionClass:
    key: str
    days: int
    deletable: bool


@dataclass(frozen=True)
class DeletionRequest:
    subject_key: str
    requested_at: datetime
    retention_class: str


@dataclass(frozen=True)
class RestorePoint:
    key: str
    created_at: datetime
    checksum: str
    source: str


@dataclass(frozen=True)
class RestoreEvidence:
    restore_point: str
    checksum_verified: bool
    isolated: bool
    completed_at: datetime


@dataclass(frozen=True)
class RegionCapability:
    region: str
    storage: bool
    processing: bool
    realtime: bool


@dataclass(frozen=True)
class RegionPolicy:
    preferred_region: str
    allowed_regions: tuple[str, ...]
    allow_failover: bool

    def can_failover_to(self, region: str) -> bool:
        return self.allow_failover and region in self.allowed_regions and region != self.preferred_region


class QueuePriority(str, Enum):
    INTERACTIVE = "interactive"
    STANDARD = "standard"
    BATCH = "batch"


@dataclass(frozen=True)
class QueueJob:
    key: str
    tenant_key: str
    priority: QueuePriority
    estimated_units: int
    enqueued_at: datetime


@dataclass(frozen=True)
class SchedulingPolicy:
    tenant_concurrency: int
    capacity_units: int

    def admit(self, job: QueueJob, used_units: int) -> bool:
        return job.estimated_units > 0 and used_units + job.estimated_units <= self.capacity_units


@dataclass(frozen=True)
class EvaluationDataset:
    key: str
    version: str
    provenance: str
    anonymized: bool
    baseline_score: float


@dataclass(frozen=True)
class ModelVersion:
    provider: str
    model: str
    version: str
    quality_score: float
    cost_score: float


@dataclass(frozen=True)
class ModelChange:
    previous: ModelVersion
    candidate: ModelVersion
    canary_score: float

    def regression(self, minimum_quality: float) -> bool:
        return self.canary_score < minimum_quality or self.candidate.quality_score < self.previous.quality_score


@dataclass(frozen=True)
class OperatingDrill:
    name: str
    owner: str
    due_at: datetime
    evidence_ref: str | None = None

    @property
    def overdue(self) -> bool:
        return datetime.now(timezone.utc) > self.due_at and not self.evidence_ref


def validate_release_manifest(manifest: ReleaseManifest) -> list[str]:
    return [] if manifest.valid() else ["release_manifest_incomplete"]


def validate_retention_class(policy: RetentionClass) -> list[str]:
    errors: list[str] = []
    if not policy.key.strip():
        errors.append("key_required")
    if policy.days < 0:
        errors.append("days_invalid")
    return errors


def validate_region_policy(policy: RegionPolicy) -> list[str]:
    errors: list[str] = []
    if not policy.preferred_region.strip():
        errors.append("preferred_region_required")
    if policy.preferred_region not in policy.allowed_regions:
        errors.append("preferred_region_not_allowed")
    return errors


def validate_evaluation_dataset(dataset: EvaluationDataset) -> list[str]:
    errors: list[str] = []
    if not dataset.key.strip() or not dataset.version.strip():
        errors.append("identity_required")
    if not dataset.provenance.strip():
        errors.append("provenance_required")
    if not dataset.anonymized:
        errors.append("anonymization_required")
    if not 0 <= dataset.baseline_score <= 100:
        errors.append("baseline_score_invalid")
    return errors


def select_restore_point(points: Iterable[RestorePoint]) -> RestorePoint | None:
    ordered = sorted(points, key=lambda item: (item.created_at, item.key), reverse=True)
    return ordered[0] if ordered else None
