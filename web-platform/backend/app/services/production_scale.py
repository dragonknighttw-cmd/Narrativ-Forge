from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import sqrt
from typing import Any, Callable, Protocol
import hashlib
import json
import time


class PublishState(str, Enum):
    PLANNED = "planned"
    READY = "ready"
    PUBLISHING = "publishing"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass(frozen=True)
class PlatformMetadata:
    platform: str
    title: str
    description: str = ""
    hashtags: tuple[str, ...] = ()
    scheduled_at: datetime | None = None


@dataclass(frozen=True)
class PublishResult:
    attempt_key: str
    platform: str
    state: PublishState
    external_id: str | None = None
    url: str | None = None
    error: str | None = None


class PublishingAdapter(Protocol):
    platform: str

    def validate_metadata(self, metadata: PlatformMetadata) -> list[str]: ...

    def publish(self, *, idempotency_key: str, media_url: str, metadata: PlatformMetadata) -> PublishResult: ...


PLATFORM_TITLE_LIMITS = {"tiktok": 2200, "youtube_shorts": 100, "facebook_reels": 255}


def validate_platform_metadata(metadata: PlatformMetadata) -> list[str]:
    errors: list[str] = []
    platform = metadata.platform.strip().lower()
    if platform not in PLATFORM_TITLE_LIMITS:
        errors.append("unsupported_platform")
        return errors
    if not metadata.title.strip():
        errors.append("title_required")
    if len(metadata.title) > PLATFORM_TITLE_LIMITS[platform]:
        errors.append("title_too_long")
    if metadata.scheduled_at and metadata.scheduled_at.tzinfo is None:
        errors.append("scheduled_at_must_be_timezone_aware")
    return errors


def build_publish_attempt_key(episode_id: str, platform: str, variant: str = "master") -> str:
    raw = f"{episode_id}:{platform.lower()}:{variant}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class IdempotentPublishLedger:
    """In-memory contract used by adapters; production storage should persist this key."""

    def __init__(self) -> None:
        self._results: dict[str, PublishResult] = {}

    def get(self, key: str) -> PublishResult | None:
        return self._results.get(key)

    def put(self, key: str, result: PublishResult) -> PublishResult:
        existing = self._results.get(key)
        if existing is not None:
            return existing
        self._results[key] = result
        return result


@dataclass(frozen=True)
class TrendRecord:
    topic: str
    score: float
    source: str
    observed_at: datetime
    expires_at: datetime | None = None
    attribution_url: str | None = None


class TrendConnector(Protocol):
    name: str

    def fetch(self, query: str | None = None) -> list[TrendRecord]: ...


class TrendRateLimitError(RuntimeError):
    pass


@dataclass
class TrendCache:
    ttl_seconds: int = 900
    _items: dict[str, tuple[float, list[TrendRecord]]] = field(default_factory=dict)

    def get(self, key: str, now: float | None = None) -> list[TrendRecord] | None:
        stamp = time.time() if now is None else now
        cached = self._items.get(key)
        if cached is None or stamp - cached[0] > self.ttl_seconds:
            return None
        return cached[1]

    def put(self, key: str, records: list[TrendRecord], now: float | None = None) -> None:
        stamp = time.time() if now is None else now
        self._items[key] = (stamp, records)


def fetch_trends_with_fallback(
    connectors: list[TrendConnector],
    *,
    query: str | None = None,
    cache: TrendCache | None = None,
    cache_key: str = "default",
) -> list[TrendRecord]:
    if cache is not None:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    for connector in connectors:
        try:
            records = connector.fetch(query)
            if cache is not None:
                cache.put(cache_key, records)
            return records
        except TrendRateLimitError:
            continue
        except Exception:
            continue
    return []


class ExperimentState(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    STOPPED = "stopped"
    WINNER_SELECTED = "winner_selected"


@dataclass(frozen=True)
class ExperimentVariant:
    key: str
    payload: dict[str, Any]


@dataclass
class Experiment:
    key: str
    variants: tuple[ExperimentVariant, ...]
    state: ExperimentState = ExperimentState.DRAFT
    allocation: dict[str, float] = field(default_factory=dict)


def validate_allocation(allocation: dict[str, float], variant_keys: set[str]) -> list[str]:
    errors = [f"unknown_variant:{key}" for key in allocation if key not in variant_keys]
    if any(value < 0 for value in allocation.values()):
        errors.append("negative_allocation")
    total = sum(allocation.values())
    if allocation and abs(total - 1.0) > 1e-6:
        errors.append("allocation_must_sum_to_one")
    if set(allocation) != variant_keys:
        errors.append("allocation_must_cover_all_variants")
    return errors


@dataclass(frozen=True)
class ExperimentOutcome:
    variant_key: str
    impressions: int
    conversions: int


def conversion_rate(outcome: ExperimentOutcome) -> float:
    return outcome.conversions / max(outcome.impressions, 1)


def _wilson_lower_bound(outcome: ExperimentOutcome, z: float = 1.96) -> float:
    n = max(outcome.impressions, 0)
    if n == 0:
        return 0.0
    p = min(max(conversion_rate(outcome), 0.0), 1.0)
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    margin = z * sqrt((p * (1 - p) + z * z / (4 * n)) / n)
    return (centre - margin) / denom


def select_experiment_winner(
    outcomes: list[ExperimentOutcome],
    *,
    min_impressions: int = 100,
    min_lift: float = 0.05,
) -> str | None:
    eligible = [item for item in outcomes if item.impressions >= min_impressions]
    if not eligible:
        return None
    ranked = sorted(eligible, key=lambda item: (-_wilson_lower_bound(item), item.variant_key))
    best = ranked[0]
    runner_up = ranked[1] if len(ranked) > 1 else None
    if runner_up is not None:
        if conversion_rate(best) < conversion_rate(runner_up) * (1 + min_lift):
            return None
    return best.variant_key


class EvaluationMetric(str, Enum):
    QUALITY = "quality"
    LATENCY = "latency"
    COST = "cost"


@dataclass(frozen=True)
class ProviderEvaluation:
    provider: str
    capability: str
    scores: dict[str, float]
    sample_count: int


def rank_ai_providers(
    evaluations: list[ProviderEvaluation],
    *,
    capability: str,
    weights: dict[str, float] | None = None,
) -> list[ProviderEvaluation]:
    weights = weights or {"quality": 0.7, "latency": 0.15, "cost": 0.15}
    candidates = [item for item in evaluations if item.capability == capability]
    def score(item: ProviderEvaluation) -> float:
        return sum(weights.get(key, 0.0) * float(item.scores.get(key, 0.0)) for key in weights)
    return sorted(candidates, key=lambda item: (-score(item), item.provider))


@dataclass(frozen=True)
class EvalCase:
    case_id: str
    input_text: str
    expected: dict[str, Any]


def stable_case_hash(case: EvalCase) -> str:
    payload = json.dumps({"id": case.case_id, "input": case.input_text, "expected": case.expected}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class TimelineClip:
    asset_key: str
    start_seconds: float
    end_seconds: float
    track: int = 0


def validate_timeline(clips: list[TimelineClip]) -> list[str]:
    errors: list[str] = []
    for clip in clips:
        if clip.start_seconds < 0 or clip.end_seconds <= clip.start_seconds:
            errors.append(f"invalid_clip:{clip.asset_key}")
    by_track: dict[int, list[TimelineClip]] = {}
    for clip in clips:
        by_track.setdefault(clip.track, []).append(clip)
    for track, items in by_track.items():
        ordered = sorted(items, key=lambda item: item.start_seconds)
        for previous, current in zip(ordered, ordered[1:]):
            if current.start_seconds < previous.end_seconds:
                errors.append(f"overlap:track={track}:{previous.asset_key}:{current.asset_key}")
    return errors


def build_edl(clips: list[TimelineClip]) -> str:
    errors = validate_timeline(clips)
    if errors:
        raise ValueError(";".join(errors))
    lines = ["TITLE: NARRATIV_FORGE", "FCM: NON-DROP FRAME"]
    for index, clip in enumerate(sorted(clips, key=lambda item: (item.track, item.start_seconds)), 1):
        lines.append(f"{index:03d}  AX       V     C        {clip.start_seconds:.3f} {clip.end_seconds:.3f} {clip.start_seconds:.3f} {clip.end_seconds:.3f}")
        lines.append(f"* FROM CLIP NAME: {clip.asset_key}")
    return "\n".join(lines) + "\n"


def build_nle_manifest(episode_id: str, clips: list[TimelineClip], *, format_name: str = "fcpxml") -> dict[str, Any]:
    errors = validate_timeline(clips)
    if errors:
        raise ValueError(";".join(errors))
    return {
        "episode_id": episode_id,
        "format": format_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "clips": [
            {"asset_key": item.asset_key, "start": item.start_seconds, "end": item.end_seconds, "track": item.track}
            for item in clips
        ],
    }


@dataclass(frozen=True)
class LifecyclePolicy:
    hot_days: int = 30
    cold_days: int = 90
    delete_after_days: int | None = None


def lifecycle_action(age_days: int, policy: LifecyclePolicy, *, is_approved_final: bool, is_referenced: bool) -> str:
    if age_days < 0:
        raise ValueError("age_days must be >= 0")
    if is_approved_final or is_referenced:
        return "retain"
    if policy.delete_after_days is not None and age_days >= policy.delete_after_days:
        return "delete"
    if age_days >= policy.cold_days:
        return "archive"
    return "hot"


@dataclass(frozen=True)
class DisasterRecoveryTarget:
    rpo_minutes: int
    rto_minutes: int


def validate_dr_target(target: DisasterRecoveryTarget) -> list[str]:
    errors: list[str] = []
    if target.rpo_minutes < 0:
        errors.append("rpo_minutes")
    if target.rto_minutes < 0:
        errors.append("rto_minutes")
    return errors


@dataclass(frozen=True)
class AlertRule:
    name: str
    metric: str
    threshold: float
    operator: str = ">="


def evaluate_alert(rule: AlertRule, value: float) -> bool:
    if rule.operator == ">=":
        return value >= rule.threshold
    if rule.operator == ">":
        return value > rule.threshold
    if rule.operator == "<=":
        return value <= rule.threshold
    if rule.operator == "<":
        return value < rule.threshold
    raise ValueError("unsupported alert operator")


def build_incident_event(name: str, severity: str, summary: str, *, now: datetime | None = None) -> dict[str, str]:
    current = now or datetime.now(timezone.utc)
    return {"name": name, "severity": severity, "summary": summary, "created_at": current.isoformat()}


@dataclass(frozen=True)
class ComplianceCheck:
    key: str
    passed: bool
    evidence_ref: str | None = None


def compliance_gate(checks: list[ComplianceCheck]) -> tuple[bool, list[str]]:
    missing = [item.key for item in checks if not item.passed]
    return not missing, missing
