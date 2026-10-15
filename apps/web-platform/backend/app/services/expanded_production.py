from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol
import hashlib
import re


class UploadState(str, Enum):
    CREATED = "created"
    UPLOADING = "uploading"
    COMPLETE = "complete"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class UploadSession:
    key: str
    filename: str
    size_bytes: int
    checksum: str | None = None
    offset: int = 0
    state: UploadState = UploadState.CREATED
    chunks: dict[int, bytes] = field(default_factory=dict)

    def accept_chunk(self, *, offset: int, data: bytes) -> int:
        if self.state in {UploadState.COMPLETE, UploadState.EXPIRED}:
            raise ValueError("upload_session_closed")
        if offset != self.offset:
            raise ValueError("offset_mismatch")
        if not data:
            raise ValueError("empty_chunk")
        if self.offset + len(data) > self.size_bytes:
            raise ValueError("upload_exceeds_declared_size")
        self.state = UploadState.UPLOADING
        self.chunks[offset] = data
        self.offset += len(data)
        return self.offset

    def finalize(self, checksum: str | None = None) -> str:
        if self.offset != self.size_bytes:
            raise ValueError("upload_incomplete")
        payload = b"".join(self.chunks[key] for key in sorted(self.chunks))
        actual = hashlib.sha256(payload).hexdigest()
        expected = checksum or self.checksum
        if expected and actual != expected:
            self.state = UploadState.FAILED
            raise ValueError("checksum_mismatch")
        self.state = UploadState.COMPLETE
        self.checksum = actual
        return actual


@dataclass(frozen=True)
class ContentVersion:
    key: str
    parent_key: str
    number: int
    kind: str
    is_final: bool = False
    notes: str = ""


def next_version_number(versions: list[ContentVersion]) -> int:
    return max((item.number for item in versions), default=0) + 1


def retained_versions(versions: list[ContentVersion], *, keep_last: int = 3) -> list[ContentVersion]:
    if keep_last < 1:
        raise ValueError("keep_last must be >= 1")
    ordered = sorted(versions, key=lambda item: item.number, reverse=True)
    keep: dict[str, ContentVersion] = {}
    for item in ordered:
        if item.is_final or len([v for v in keep.values() if v.parent_key == item.parent_key]) < keep_last:
            keep[item.key] = item
    return sorted(keep.values(), key=lambda item: item.number)


@dataclass(frozen=True)
class HookCandidate:
    text: str
    hook_type: str
    score: float


HOOK_TYPES = (
    "question", "shock", "mystery", "warning",
    "personal_story", "contrarian", "cliffhanger", "number",
)


def rank_hook_candidates(candidates: list[HookCandidate], limit: int = 3) -> list[HookCandidate]:
    return sorted(candidates, key=lambda item: (-item.score, item.text))[:limit]


@dataclass(frozen=True)
class StorySplitPlan:
    episode_number: int
    title: str
    duration_seconds: int
    scenes: tuple[str, ...]
    characters: tuple[str, ...]
    cliffhanger: str


def validate_story_split_plan(plan: StorySplitPlan) -> list[str]:
    errors: list[str] = []
    if plan.episode_number < 1:
        errors.append("episode_number")
    if not 1 <= plan.duration_seconds <= 600:
        errors.append("duration_seconds")
    if not plan.title.strip():
        errors.append("title")
    if not plan.scenes:
        errors.append("scenes")
    return errors


@dataclass(frozen=True)
class SeoMetadata:
    title: str
    caption: str
    keywords: tuple[str, ...]
    hashtags: tuple[str, ...]
    posting_window: str | None = None


def validate_seo(metadata: SeoMetadata) -> list[str]:
    errors: list[str] = []
    if not metadata.title.strip():
        errors.append("title_required")
    if len(metadata.title) > 2200:
        errors.append("title_too_long")
    if not metadata.keywords:
        errors.append("keywords_required")
    return errors


@dataclass(frozen=True)
class RetentionAssessment:
    pacing_score: float
    hook_score: float
    emotional_arc: tuple[str, ...]
    warnings: tuple[str, ...] = ()


def assess_retention(*, duration_seconds: int, scene_count: int, hook_score: float, arc: tuple[str, ...]) -> RetentionAssessment:
    if duration_seconds <= 0 or scene_count <= 0:
        raise ValueError("duration and scene_count must be positive")
    pacing = min(100.0, max(0.0, scene_count / duration_seconds * 1800))
    warnings: list[str] = []
    if hook_score < 60:
        warnings.append("weak_hook")
    if duration_seconds > 180:
        warnings.append("duration_above_target")
    if len(arc) < 3:
        warnings.append("emotional_arc_too_short")
    return RetentionAssessment(pacing, hook_score, arc, tuple(warnings))


@dataclass(frozen=True)
class ThumbnailCandidate:
    asset_key: str
    score: float
    reason: str


def select_thumbnail_candidates(candidates: list[ThumbnailCandidate], count: int = 5) -> list[ThumbnailCandidate]:
    return sorted(candidates, key=lambda item: (-item.score, item.asset_key))[:count]


@dataclass(frozen=True)
class SoundDesignPlan:
    intro: str
    hook_impact: str
    transitions: str
    climax: str
    outro: str
    bgm_mood: str


@dataclass(frozen=True)
class SeriesBible:
    series_id: str
    title: str
    genre: str
    characters: tuple[str, ...]
    world_setting: str
    tone: str
    visual_style: str
    continuity_rules: tuple[str, ...]


@dataclass(frozen=True)
class ContinuityIssue:
    category: str
    message: str
    severity: str = "warning"


def check_continuity(*, expected_characters: set[str], actual_characters: set[str],
                     expected_locations: set[str], actual_locations: set[str]) -> list[ContinuityIssue]:
    issues: list[ContinuityIssue] = []
    for name in sorted(actual_characters - expected_characters):
        issues.append(ContinuityIssue("character", f"unexpected_character:{name}"))
    for name in sorted(actual_locations - expected_locations):
        issues.append(ContinuityIssue("location", f"unexpected_location:{name}"))
    for name in sorted(expected_characters - actual_characters):
        issues.append(ContinuityIssue("character", f"missing_character:{name}"))
    for name in sorted(expected_locations - actual_locations):
        issues.append(ContinuityIssue("location", f"missing_location:{name}"))
    return issues


@dataclass(frozen=True)
class CalendarEntry:
    episode_key: str
    scheduled_date: str
    scheduled_time: str
    metadata_ready: bool = False


def validate_calendar(entries: list[CalendarEntry]) -> list[str]:
    seen: set[tuple[str, str]] = set()
    errors: list[str] = []
    for item in entries:
        key = (item.scheduled_date, item.scheduled_time)
        if key in seen:
            errors.append(f"schedule_collision:{item.scheduled_date}:{item.scheduled_time}")
        seen.add(key)
    return errors


@dataclass(frozen=True)
class BatchPlan:
    episode_keys: tuple[str, ...]
    approved: bool
    max_daily_units: int


def validate_batch_plan(plan: BatchPlan) -> list[str]:
    errors: list[str] = []
    if not plan.episode_keys:
        errors.append("empty_batch")
    if len(plan.episode_keys) > 5:
        errors.append("batch_limit_exceeded")
    if plan.max_daily_units < 1:
        errors.append("invalid_daily_limit")
    if not plan.approved:
        errors.append("human_approval_required")
    return errors


@dataclass(frozen=True)
class TranslationRequest:
    source_language: str
    target_language: str
    text: str
    preserve_line_breaks: bool = True


def validate_translation(request: TranslationRequest) -> list[str]:
    errors: list[str] = []
    if request.source_language != "my":
        errors.append("burmese_source_required")
    if request.target_language not in {"en", "th", "zh"}:
        errors.append("unsupported_target")
    if not request.text:
        errors.append("text_required")
    return errors


class VideoGenerationAdapter(Protocol):
    provider: str

    def validate(self, *, commercial_use: bool, watermark_free_required: bool) -> list[str]: ...


@dataclass(frozen=True)
class WatermarkPolicy:
    commercial_use: bool
    watermark_free_required: bool


def evaluate_watermark_policy(*, provider: str, watermark_present: bool, policy: WatermarkPolicy) -> list[str]:
    if watermark_present and policy.watermark_free_required:
        return [f"watermark_not_allowed:{provider}"]
    if policy.commercial_use and watermark_present:
        return [f"commercial_watermark_review_required:{provider}"]
    return []


def stable_expansion_id(payload: dict[str, Any]) -> str:
    normalized = repr(sorted(payload.items())).encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()
