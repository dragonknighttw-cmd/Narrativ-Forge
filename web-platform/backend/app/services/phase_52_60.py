"""Code-only contracts for the next product backlog phases (52–60).

These contracts deliberately avoid provider credentials and live acceptance claims.
They make the remaining work testable before external/live gates are available.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal


Status = Literal["draft", "pending", "approved", "rejected", "verified", "blocked"]


@dataclass(frozen=True)
class TrailerPlan:
    series_id: str
    duration_seconds: int
    beats: tuple[str, ...]
    hook: str
    approval: Status = "draft"

    def valid(self) -> bool:
        return bool(self.series_id.strip() and self.hook.strip() and 10 <= self.duration_seconds <= 180 and self.beats)


@dataclass(frozen=True)
class TranslationTerm:
    source: str
    target: str
    language: str
    glossary_version: str
    status: Status = "pending"

    def valid(self) -> bool:
        return bool(self.source.strip() and self.target.strip() and self.language.strip() and self.glossary_version.strip())


def normalize_subtitle_text(text: str) -> str:
    text = re.sub(r"[\t\r ]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


@dataclass(frozen=True)
class AudioCue:
    track_id: str
    start_ms: int
    end_ms: int
    gain_db: float = 0.0
    duck_db: float = 0.0

    def valid(self) -> bool:
        return bool(self.track_id.strip()) and 0 <= self.start_ms < self.end_ms and -60 <= self.gain_db <= 12 and 0 <= self.duck_db <= 30


@dataclass(frozen=True)
class AudioTrack:
    track_id: str
    rights_ref: str
    loudness_lufs: float
    cues: tuple[AudioCue, ...] = ()

    def valid(self) -> bool:
        return bool(self.track_id.strip() and self.rights_ref.strip() and -60 <= self.loudness_lufs <= 0 and all(c.valid() for c in self.cues))


@dataclass(frozen=True)
class ThumbnailCandidate:
    candidate_id: str
    asset_ref: str
    score: float
    rank: int
    selected: bool = False

    def valid(self) -> bool:
        return bool(self.candidate_id.strip() and self.asset_ref.strip() and 0 <= self.score <= 1 and 1 <= self.rank <= 10)


def select_thumbnail_shortlist(candidates: tuple[ThumbnailCandidate, ...], limit: int = 5) -> tuple[ThumbnailCandidate, ...]:
    valid = [c for c in candidates if c.valid()]
    return tuple(sorted(valid, key=lambda c: (-c.score, c.rank, c.candidate_id))[: max(1, limit)])


@dataclass(frozen=True)
class ConsistencyProfile:
    profile_id: str
    model_version: str
    identity_refs: tuple[str, ...]
    commercial_use: Status = "pending"

    def valid(self) -> bool:
        return bool(self.profile_id.strip() and self.model_version.strip() and self.identity_refs)


@dataclass(frozen=True)
class SocialAnalyticsEvent:
    source: str
    external_event_id: str
    metric: str
    value: float
    occurred_at: str

    def idempotency_key(self) -> str:
        return f"{self.source.strip().lower()}:{self.external_event_id.strip()}"

    def valid(self) -> bool:
        return bool(self.source.strip() and self.external_event_id.strip() and self.metric.strip() and self.occurred_at.strip() and self.value >= 0)


@dataclass(frozen=True)
class ArchiveRecord:
    asset_id: str
    retention_class: str
    legal_hold: bool
    encrypted: bool
    purge_after: str | None = None

    def purge_allowed(self) -> bool:
        return bool(self.asset_id.strip() and self.encrypted and not self.legal_hold and self.purge_after)


@dataclass(frozen=True)
class ManualValidation:
    episode_id: str
    evidence_refs: tuple[str, ...]
    measured_seconds: float
    repeated_problem_tags: tuple[str, ...] = ()
    accepted: bool = False

    def valid(self) -> bool:
        return bool(self.episode_id.strip() and self.evidence_refs and self.measured_seconds >= 0)


@dataclass(frozen=True)
class UIStateAudit:
    route: str
    states: tuple[str, ...]
    accessibility_checked: bool
    responsive_checked: bool
    evidence_ref: str | None = None

    def complete(self) -> bool:
        required = {"loading", "empty", "error", "success"}
        return bool(self.route.strip() and required.issubset(set(self.states)) and self.accessibility_checked and self.responsive_checked and self.evidence_ref)


def validate_next_phase_inputs(
    trailer: TrailerPlan,
    translation: TranslationTerm,
    audio: AudioTrack,
    consistency: ConsistencyProfile,
    social: SocialAnalyticsEvent,
    archive: ArchiveRecord,
    manual: ManualValidation,
    ui: UIStateAudit,
) -> list[str]:
    errors: list[str] = []
    if not trailer.valid(): errors.append("trailer_invalid")
    if not translation.valid(): errors.append("translation_invalid")
    if not audio.valid(): errors.append("audio_invalid")
    if not consistency.valid(): errors.append("consistency_invalid")
    if not social.valid(): errors.append("social_event_invalid")
    if not archive.purge_allowed(): errors.append("archive_purge_blocked")
    if not manual.valid(): errors.append("manual_validation_invalid")
    if not ui.complete(): errors.append("ui_audit_incomplete")
    return errors
