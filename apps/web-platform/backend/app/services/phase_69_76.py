"""Code-only foundations for the Phase 69-76 release-operations backlog."""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from typing import Sequence


@dataclass(frozen=True)
class RolloutPolicy:
    feature: str
    cohorts: tuple[str, ...]
    max_percent: int
    rollback_percent: int = 0

    def valid(self) -> bool:
        return bool(self.feature.strip() and self.cohorts and 0 <= self.rollback_percent <= self.max_percent <= 100)


@dataclass(frozen=True)
class SchemaDrift:
    table: str
    expected_columns: tuple[str, ...]
    actual_columns: tuple[str, ...]

    @property
    def missing(self) -> tuple[str, ...]:
        return tuple(c for c in self.expected_columns if c not in self.actual_columns)

    @property
    def unexpected(self) -> tuple[str, ...]:
        return tuple(c for c in self.actual_columns if c not in self.expected_columns)

    def compatible(self) -> bool:
        return not self.missing


@dataclass(frozen=True)
class RestoreVerification:
    backup_ref: str
    restored_ref: str
    checksum_match: bool
    migration_head: str
    expected_head: str

    def verified(self) -> bool:
        return bool(self.backup_ref.strip() and self.restored_ref.strip() and self.checksum_match and self.migration_head == self.expected_head)


@dataclass(frozen=True)
class PrivacyRequest:
    subject_id: str
    request_type: str
    legal_basis: str
    completed: bool
    evidence_ref: str = ""

    def valid(self) -> bool:
        return bool(self.subject_id.strip() and self.request_type in {"access", "export", "rectification", "erasure", "restriction"} and self.legal_basis.strip())

    def closed(self) -> bool:
        return self.valid() and self.completed and bool(self.evidence_ref.strip())


@dataclass(frozen=True)
class SecretRequirement:
    name: str
    required: bool
    configured: bool
    source: str = ""

    def ready(self) -> bool:
        return bool(self.name.strip()) and (not self.required or (self.configured and bool(self.source.strip())))


@dataclass(frozen=True)
class DependencyLicense:
    package: str
    version: str
    license_id: str
    allowed: bool

    def valid(self) -> bool:
        return bool(self.package.strip() and self.version.strip() and self.license_id.strip())


@dataclass(frozen=True)
class ChaosDrill:
    scenario: str
    expected_recovery_seconds: int
    observed_recovery_seconds: int | None
    rollback_tested: bool

    def passed(self) -> bool:
        return self.observed_recovery_seconds is not None and self.observed_recovery_seconds <= self.expected_recovery_seconds and self.rollback_tested


@dataclass(frozen=True)
class EvidencePack:
    release_sha: str
    evidence_refs: tuple[str, ...]
    blocking_gates: tuple[str, ...] = ()

    @property
    def fingerprint(self) -> str:
        return sha256("|".join((self.release_sha, *sorted(self.evidence_refs))).encode()).hexdigest()

    def ready(self) -> bool:
        return len(self.release_sha) == 40 and bool(self.evidence_refs) and not self.blocking_gates


def validate_release_operations(
    rollout: RolloutPolicy,
    drift: SchemaDrift,
    restore: RestoreVerification,
    privacy: PrivacyRequest,
    secrets: Sequence[SecretRequirement],
    licenses: Sequence[DependencyLicense],
    drill: ChaosDrill,
    evidence: EvidencePack,
) -> list[str]:
    errors: list[str] = []
    if not rollout.valid(): errors.append("rollout_invalid")
    if not drift.compatible(): errors.append("schema_drift")
    if not restore.verified(): errors.append("restore_unverified")
    if not privacy.closed(): errors.append("privacy_request_open")
    if not all(s.ready() for s in secrets): errors.append("secret_requirements_unready")
    if not all(x.valid() and x.allowed for x in licenses): errors.append("license_blocked")
    if not drill.passed(): errors.append("chaos_drill_failed")
    if not evidence.ready(): errors.append("evidence_pack_blocked")
    return errors
