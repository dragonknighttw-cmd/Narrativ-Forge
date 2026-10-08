from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any


@dataclass(frozen=True)
class ExportManifest:
    platform: str
    episode_key: str
    title: str
    caption: str
    hashtags: tuple[str, ...]
    scheduled_at: str | None = None
    idempotency_key: str = ""

    def key(self) -> str:
        if self.idempotency_key:
            return self.idempotency_key
        raw = json.dumps(self.__dict__, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()


def validate_export_manifest(manifest: ExportManifest) -> list[str]:
    errors: list[str] = []
    if not manifest.platform.strip(): errors.append("platform_required")
    if not manifest.episode_key.strip(): errors.append("episode_required")
    if not manifest.title.strip(): errors.append("title_required")
    if len(manifest.title) > 2200: errors.append("title_too_long")
    if not manifest.hashtags: errors.append("hashtags_required")
    return errors


@dataclass(frozen=True)
class CachedTrend:
    provider: str
    key: str
    value: tuple[str, ...]
    fetched_at: datetime
    ttl_seconds: int = 900

    def fresh(self, *, now: datetime | None = None) -> bool:
        current = now or datetime.now(timezone.utc)
        return (current - self.fetched_at).total_seconds() < self.ttl_seconds


@dataclass(frozen=True)
class ExperimentVariant:
    key: str
    weight: float


@dataclass(frozen=True)
class Experiment:
    key: str
    variants: tuple[ExperimentVariant, ...]
    min_samples: int = 30
    active: bool = True


def validate_experiment(experiment: Experiment) -> list[str]:
    errors: list[str] = []
    if not experiment.key.strip(): errors.append("key_required")
    if not experiment.variants: errors.append("variants_required")
    if len({v.key for v in experiment.variants}) != len(experiment.variants): errors.append("duplicate_variant_key")
    if abs(sum(v.weight for v in experiment.variants) - 1.0) > 1e-6: errors.append("weights_must_sum_to_one")
    if any(v.weight < 0 for v in experiment.variants): errors.append("negative_weight")
    if experiment.min_samples < 1: errors.append("min_samples")
    return errors


def choose_experiment_winner(results: dict[str, float], *, sample_count: int, min_samples: int) -> str | None:
    if sample_count < min_samples or not results:
        return None
    return max(sorted(results), key=lambda key: results[key])


@dataclass(frozen=True)
class ProviderQualityScore:
    provider: str
    quality: float
    latency_ms: float
    cost: float

    def rank_score(self) -> float:
        return self.quality * 0.65 + max(0.0, 100.0 - self.latency_ms / 20.0) * 0.20 + max(0.0, 100.0 - self.cost) * 0.15


def rank_providers(scores: list[ProviderQualityScore]) -> list[ProviderQualityScore]:
    return sorted(scores, key=lambda item: (-item.rank_score(), item.provider))


@dataclass(frozen=True)
class NLEManifest:
    format: str
    fps: float
    duration_seconds: float
    clips: tuple[dict[str, Any], ...]


def validate_nle_manifest(manifest: NLEManifest) -> list[str]:
    errors: list[str] = []
    if manifest.format not in {"edl", "fcpxml"}: errors.append("unsupported_format")
    if manifest.fps <= 0: errors.append("invalid_fps")
    if manifest.duration_seconds <= 0: errors.append("invalid_duration")
    previous_end = 0.0
    for clip in manifest.clips:
        start = float(clip.get("start", -1))
        end = float(clip.get("end", -1))
        if start < previous_end: errors.append("clip_overlap")
        if end <= start: errors.append("invalid_clip_range")
        previous_end = max(previous_end, end)
    return errors


class IncidentSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class IncidentEvent:
    key: str
    severity: IncidentSeverity
    message: str
    evidence_refs: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class CollaborationLock:
    resource_key: str
    owner_key: str
    version: int


def validate_lock(current_version: int, lock: CollaborationLock) -> None:
    if lock.version != current_version:
        raise ValueError("optimistic_lock_conflict")


@dataclass(frozen=True)
class PresenceEvent:
    user_key: str
    resource_key: str
    event: str
    at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class UsageReservation:
    tenant_key: str
    metric: str
    amount: int
    idempotency_key: str


def validate_usage_reservation(reservation: UsageReservation) -> list[str]:
    errors: list[str] = []
    if reservation.amount < 1: errors.append("amount")
    if not reservation.tenant_key.strip(): errors.append("tenant_key")
    if not reservation.metric.strip(): errors.append("metric")
    if not reservation.idempotency_key.strip(): errors.append("idempotency_key")
    return errors


@dataclass(frozen=True)
class SupportDiagnostic:
    request_id: str
    redacted_fields: tuple[str, ...]
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class LaunchEvidence:
    gate: str
    status: str
    evidence_refs: tuple[str, ...] = ()


def launch_summary(evidence: list[LaunchEvidence]) -> dict[str, Any]:
    blocked = sorted(item.gate for item in evidence if item.status.lower() not in {"verified", "waived"})
    return {"ready": not blocked, "blocked_gates": blocked, "count": len(evidence)}
