from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import hashlib


@dataclass(frozen=True)
class CharacterProfile:
    key: str
    name: str
    traits: tuple[str, ...] = ()
    voice_notes: str = ""


@dataclass(frozen=True)
class StyleProfile:
    key: str
    visual_rules: tuple[str, ...] = ()
    subtitle_rules: tuple[str, ...] = ()
    audio_rules: tuple[str, ...] = ()


@dataclass(frozen=True)
class EpisodeScore:
    hook: float
    retention: float
    continuity: float
    production_cost: float

    @property
    def total(self) -> float:
        return (self.hook * 0.35) + (self.retention * 0.35) + (self.continuity * 0.20) + (self.production_cost * 0.10)


@dataclass(frozen=True)
class SubtitleQualityCase:
    case_id: str
    source: str
    normalized: str
    expected_script: str
    expected_zawgyi: bool


def fingerprint_quality_case(case: SubtitleQualityCase) -> str:
    raw = f"{case.case_id}|{case.source}|{case.normalized}|{case.expected_script}|{case.expected_zawgyi}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def score_subtitle_case(*, timing_ok: bool, unicode_ok: bool, line_length_ok: bool, overlap_free: bool) -> float:
    checks = (timing_ok, unicode_ok, line_length_ok, overlap_free)
    return sum(checks) / len(checks) * 100.0


@dataclass(frozen=True)
class Dependency:
    source_key: str
    output_key: str


def affected_by_change(changed_key: str, dependencies: list[Dependency]) -> set[str]:
    affected: set[str] = {changed_key}
    frontier = [changed_key]
    while frontier:
        current = frontier.pop()
        for edge in dependencies:
            if edge.source_key == current and edge.output_key not in affected:
                affected.add(edge.output_key)
                frontier.append(edge.output_key)
    return affected


@dataclass(frozen=True)
class RegenerationPlan:
    changed_key: str
    invalidated_keys: tuple[str, ...]
    preserved_keys: tuple[str, ...]


def build_regeneration_plan(changed_key: str, dependencies: list[Dependency], existing_keys: list[str]) -> RegenerationPlan:
    invalidated = affected_by_change(changed_key, dependencies)
    return RegenerationPlan(
        changed_key=changed_key,
        invalidated_keys=tuple(sorted(invalidated & set(existing_keys))),
        preserved_keys=tuple(sorted(set(existing_keys) - invalidated)),
    )


@dataclass(frozen=True)
class QuotaBudget:
    key: str
    limit: int
    used: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.limit - self.used)

    def can_reserve(self, amount: int) -> bool:
        return amount > 0 and amount <= self.remaining


@dataclass(frozen=True)
class BatchJob:
    key: str
    estimated_units: int
    priority: int = 100


def plan_quota_aware_batch(jobs: list[BatchJob], budgets: list[QuotaBudget]) -> list[BatchJob]:
    remaining = {budget.key: budget.remaining for budget in budgets}
    if not remaining:
        return []
    ordered = sorted(jobs, key=lambda item: (item.priority, item.key))
    result: list[BatchJob] = []
    default_budget = next(iter(remaining))
    for job in ordered:
        if job.estimated_units <= remaining[default_budget]:
            result.append(job)
            remaining[default_budget] -= job.estimated_units
    return result


@dataclass
class ReviewLearningEvent:
    decision: str
    issue_keys: tuple[str, ...] = ()
    quality_score: float | None = None


@dataclass
class ReviewLearningModel:
    issue_counts: dict[str, int] = field(default_factory=dict)
    decisions: dict[str, int] = field(default_factory=dict)

    def ingest(self, event: ReviewLearningEvent) -> None:
        self.decisions[event.decision] = self.decisions.get(event.decision, 0) + 1
        for issue in event.issue_keys:
            self.issue_counts[issue] = self.issue_counts.get(issue, 0) + 1

    def top_issues(self, limit: int = 10) -> list[tuple[str, int]]:
        return sorted(self.issue_counts.items(), key=lambda item: (-item[1], item[0]))[:limit]


@dataclass(frozen=True)
class Presence:
    user_key: str
    resource_key: str
    connected_at: datetime


def build_presence(user_key: str, resource_key: str, *, now: datetime | None = None) -> Presence:
    return Presence(user_key=user_key, resource_key=resource_key, connected_at=now or datetime.now(timezone.utc))


@dataclass(frozen=True)
class UsageQuota:
    resource: str
    limit: int
    consumed: int

    @property
    def allowed(self) -> bool:
        return self.consumed < self.limit


def enforce_usage_quota(quota: UsageQuota, requested: int = 1) -> None:
    if requested < 1:
        raise ValueError("requested must be >= 1")
    if quota.consumed + requested > quota.limit:
        raise PermissionError(f"quota_exceeded:{quota.resource}")


@dataclass(frozen=True)
class EnterprisePolicy:
    max_storage_bytes: int
    max_concurrent_jobs: int
    allowed_roles: tuple[str, ...]


def validate_enterprise_policy(policy: EnterprisePolicy) -> list[str]:
    errors: list[str] = []
    if policy.max_storage_bytes <= 0:
        errors.append("max_storage_bytes")
    if policy.max_concurrent_jobs <= 0:
        errors.append("max_concurrent_jobs")
    if not policy.allowed_roles:
        errors.append("allowed_roles")
    return errors


@dataclass(frozen=True)
class DemoSeed:
    series_key: str
    episode_keys: tuple[str, ...]
    script_keys: tuple[str, ...]
    subtitle_keys: tuple[str, ...]


def build_demo_seed(series_key: str, episode_count: int = 3) -> DemoSeed:
    if episode_count < 1:
        raise ValueError("episode_count must be >= 1")
    episodes = tuple(f"{series_key}-ep-{index}" for index in range(1, episode_count + 1))
    return DemoSeed(
        series_key=series_key,
        episode_keys=episodes,
        script_keys=tuple(f"{key}-script" for key in episodes),
        subtitle_keys=tuple(f"{key}-srt" for key in episodes),
    )


@dataclass(frozen=True)
class LaunchGate:
    key: str
    passed: bool
    evidence: str | None = None


def evaluate_launch_gate(gates: list[LaunchGate]) -> tuple[bool, list[str]]:
    missing = [gate.key for gate in gates if not gate.passed]
    return not missing, missing
