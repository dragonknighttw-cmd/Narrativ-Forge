from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Iterable, Mapping
import hashlib
import re


class WorkflowState(str, Enum):
    EMPTY = "empty"
    LOADING = "loading"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    REJECTED = "rejected"
    OFFLINE = "offline"
    READ_ONLY = "read_only"
    PERMISSION_DENIED = "permission_denied"
    SESSION_EXPIRED = "session_expired"
    DRIVE_DISCONNECTED = "drive_disconnected"
    DRIVE_EXPORT_FAILED = "drive_export_failed"
    STORAGE_WARNING = "storage_warning"
    UNSUPPORTED_FILE = "unsupported_file"
    CRITICAL_QUALITY_ISSUE = "critical_quality_issue"


REQUIRED_UI_STATES = tuple(state.value for state in WorkflowState)


@dataclass(frozen=True)
class StatePresentation:
    state: WorkflowState
    title_key: str
    action_key: str | None
    blocking: bool = False


def build_state_matrix() -> tuple[StatePresentation, ...]:
    return tuple(
        StatePresentation(
            state=state,
            title_key=f"state.{state.value}.title",
            action_key=None if state in {
                WorkflowState.COMPLETED,
                WorkflowState.LOADING,
            } else f"state.{state.value}.action",
            blocking=state in {
                WorkflowState.FAILED,
                WorkflowState.REJECTED,
                WorkflowState.PERMISSION_DENIED,
                WorkflowState.SESSION_EXPIRED,
                WorkflowState.DRIVE_DISCONNECTED,
                WorkflowState.DRIVE_EXPORT_FAILED,
                WorkflowState.UNSUPPORTED_FILE,
                WorkflowState.CRITICAL_QUALITY_ISSUE,
            },
        )
        for state in WorkflowState
    )


@dataclass(frozen=True)
class ContentVersionRecord:
    key: str
    parent_key: str
    version: int
    created_at: datetime
    checksum: str
    is_current: bool = False
    is_final: bool = False
    immutable: bool = True


def version_checksum(parent_key: str, version: int, content: str) -> str:
    payload = f"{parent_key}:{version}:{content}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def create_content_version(
    *,
    parent_key: str,
    content: str,
    existing: Iterable[ContentVersionRecord] = (),
    now: datetime | None = None,
) -> ContentVersionRecord:
    versions = list(existing)
    number = max((item.version for item in versions), default=0) + 1
    return ContentVersionRecord(
        key=f"{parent_key}:v{number}",
        parent_key=parent_key,
        version=number,
        created_at=now or datetime.now(timezone.utc),
        checksum=version_checksum(parent_key, number, content),
        is_current=True,
    )


def retain_versions(
    versions: Iterable[ContentVersionRecord],
    *,
    keep_last: int = 3,
) -> tuple[ContentVersionRecord, ...]:
    if keep_last < 1:
        raise ValueError("keep_last must be >= 1")
    ordered = sorted(versions, key=lambda item: item.version, reverse=True)
    retained: list[ContentVersionRecord] = []
    seen_by_parent: dict[str, int] = {}
    for item in ordered:
        count = seen_by_parent.get(item.parent_key, 0)
        if item.is_final or count < keep_last:
            retained.append(item)
            seen_by_parent[item.parent_key] = count + 1
    return tuple(sorted(retained, key=lambda item: (item.parent_key, item.version)))


@dataclass(frozen=True)
class RegenerationDependency:
    source_key: str
    output_key: str
    invalidation_scope: str = "downstream"


def plan_selective_regeneration(
    changed_keys: Iterable[str],
    dependencies: Iterable[RegenerationDependency],
    existing_outputs: Iterable[str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    changed = set(changed_keys)
    edges = list(dependencies)
    invalidated = set(changed)
    frontier = list(changed)
    while frontier:
        current = frontier.pop()
        for edge in edges:
            if edge.source_key == current and edge.output_key not in invalidated:
                invalidated.add(edge.output_key)
                frontier.append(edge.output_key)
    existing = set(existing_outputs)
    return tuple(sorted(invalidated & existing)), tuple(sorted(existing - invalidated))


@dataclass
class TokenBucket:
    capacity: int
    refill_per_second: float
    tokens: float | None = None
    last_refill: float = 0.0

    def allow(self, *, cost: float = 1.0, now: float) -> bool:
        if cost <= 0:
            raise ValueError("cost must be > 0")
        if self.capacity <= 0 or self.refill_per_second < 0:
            raise ValueError("invalid bucket configuration")
        if self.tokens is None:
            self.tokens = float(self.capacity)
            self.last_refill = now
        elapsed = max(0.0, now - self.last_refill)
        self.tokens = min(
            float(self.capacity),
            self.tokens + elapsed * self.refill_per_second,
        )
        self.last_refill = now
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True


@dataclass(frozen=True)
class QuotaDecision:
    allowed: bool
    remaining: int
    reason: str | None = None


def decide_quota(*, limit: int, consumed: int, requested: int = 1) -> QuotaDecision:
    if limit < 0 or consumed < 0 or requested < 1:
        raise ValueError("invalid quota values")
    remaining = max(0, limit - consumed)
    if requested > remaining:
        return QuotaDecision(False, remaining, "quota_exceeded")
    return QuotaDecision(True, remaining - requested)


@dataclass(frozen=True)
class StorageObject:
    key: str
    size_bytes: int
    created_at: datetime
    referenced: bool = False
    final: bool = False
    archived: bool = False


@dataclass(frozen=True)
class RetentionPolicy:
    keep_days: int = 30
    archive_after_days: int = 14
    preserve_final: bool = True


def plan_storage_cleanup(
    objects: Iterable[StorageObject],
    *,
    policy: RetentionPolicy,
    now: datetime | None = None,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if policy.keep_days < 1 or policy.archive_after_days < 0:
        raise ValueError("invalid retention policy")
    current = now or datetime.now(timezone.utc)
    archive: list[str] = []
    delete: list[str] = []
    for item in objects:
        age_days = (current - item.created_at).total_seconds() / 86400
        if item.referenced or (policy.preserve_final and item.final):
            continue
        if age_days >= policy.keep_days:
            delete.append(item.key)
        elif age_days >= policy.archive_after_days and not item.archived:
            archive.append(item.key)
    return tuple(sorted(archive)), tuple(sorted(delete))


@dataclass(frozen=True)
class StorageThreshold:
    name: str
    fraction: float
    severity: str


STORAGE_THRESHOLDS = (
    StorageThreshold("warning", 0.80, "warning"),
    StorageThreshold("critical", 0.90, "critical"),
    StorageThreshold("emergency", 0.95, "emergency"),
)


def storage_threshold(*, used_bytes: int, capacity_bytes: int) -> StorageThreshold | None:
    if capacity_bytes <= 0 or used_bytes < 0:
        raise ValueError("invalid storage values")
    fraction = used_bytes / capacity_bytes
    reached = [item for item in STORAGE_THRESHOLDS if fraction >= item.fraction]
    return reached[-1] if reached else None


@dataclass(frozen=True)
class AlertRule:
    key: str
    threshold: float
    comparison: str
    severity: str


def evaluate_alert(rule: AlertRule, value: float) -> bool:
    if rule.comparison == "gte":
        return value >= rule.threshold
    if rule.comparison == "gt":
        return value > rule.threshold
    if rule.comparison == "lte":
        return value <= rule.threshold
    if rule.comparison == "lt":
        return value < rule.threshold
    raise ValueError("unsupported comparison")


@dataclass(frozen=True)
class AuditEvent:
    actor_key: str
    organization_key: str
    action: str
    resource_key: str
    occurred_at: datetime
    metadata: Mapping[str, str] = field(default_factory=dict)


def redact_audit_metadata(metadata: Mapping[str, str]) -> dict[str, str]:
    secret_words = re.compile(r"(token|secret|password|api[_-]?key|authorization|cookie)", re.I)
    return {
        key: "[REDACTED]" if secret_words.search(key) else value
        for key, value in metadata.items()
    }


@dataclass(frozen=True)
class PresenceLease:
    user_key: str
    resource_key: str
    expires_at: datetime


def issue_presence_lease(
    *,
    user_key: str,
    resource_key: str,
    ttl_seconds: int = 30,
    now: datetime | None = None,
) -> PresenceLease:
    if ttl_seconds < 1:
        raise ValueError("ttl_seconds must be >= 1")
    issued = now or datetime.now(timezone.utc)
    return PresenceLease(
        user_key=user_key,
        resource_key=resource_key,
        expires_at=issued + timedelta(seconds=ttl_seconds),
    )


@dataclass(frozen=True)
class NotificationEvent:
    event_key: str
    organization_key: str
    recipient_keys: tuple[str, ...]
    kind: str
    resource_key: str
    payload: Mapping[str, str]


def notification_key(kind: str, resource_key: str) -> str:
    return hashlib.sha256(f"{kind}:{resource_key}".encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class LegalDocumentRequirement:
    key: str
    required_for_production: bool = True


LEGAL_DOCUMENTS = (
    LegalDocumentRequirement("terms"),
    LegalDocumentRequirement("privacy"),
    LegalDocumentRequirement("dpa"),
    LegalDocumentRequirement("dmca"),
)


def legal_release_blockers(
    completed: Mapping[str, bool],
    requirements: Iterable[LegalDocumentRequirement] = LEGAL_DOCUMENTS,
) -> tuple[str, ...]:
    return tuple(
        item.key
        for item in requirements
        if item.required_for_production and not completed.get(item.key, False)
    )


@dataclass(frozen=True)
class ReleaseEvidence:
    key: str
    automated: bool = False
    live_verified: bool = False
    reserved: bool = False


def release_gate(evidence: Iterable[ReleaseEvidence]) -> tuple[bool, tuple[str, ...]]:
    missing = tuple(
        item.key
        for item in evidence
        if not (item.automated or item.live_verified or item.reserved)
    )
    return not missing, missing


@dataclass(frozen=True)
class E2EStep:
    key: str
    required: bool = True


DEFAULT_PRODUCTION_E2E = (
    E2EStep("auth"),
    E2EStep("tenant_scope"),
    E2EStep("idea"),
    E2EStep("script"),
    E2EStep("asset_upload"),
    E2EStep("queue"),
    E2EStep("worker"),
    E2EStep("ffmpeg_whisper"),
    E2EStep("subtitle_review"),
    E2EStep("approval"),
    E2EStep("drive_export"),
)


def validate_e2e_evidence(
    completed_steps: Iterable[str],
    steps: Iterable[E2EStep] = DEFAULT_PRODUCTION_E2E,
) -> tuple[bool, tuple[str, ...]]:
    completed = set(completed_steps)
    missing = tuple(step.key for step in steps if step.required and step.key not in completed)
    return not missing, missing
