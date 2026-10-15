import pytest

from app.services.code_completion import (
    AlertRule,
    DEFAULT_PRODUCTION_E2E,
    RegenerationDependency,
    RetentionPolicy,
    StorageObject,
    TokenBucket,
    WorkflowState,
    build_state_matrix,
    decide_quota,
    evaluate_alert,
    legal_release_blockers,
    plan_selective_regeneration,
    plan_storage_cleanup,
    redact_audit_metadata,
    release_gate,
    storage_threshold,
)


pytestmark = pytest.mark.unit


def test_ui_state_matrix_covers_required_states():
    states = {item.state for item in build_state_matrix()}
    assert states == set(WorkflowState)
    assert {item.state.value for item in build_state_matrix()} == {
        "empty", "loading", "uploading", "processing", "completed", "failed",
        "retrying", "rejected", "offline", "read_only", "permission_denied",
        "session_expired", "drive_disconnected", "drive_export_failed",
        "storage_warning", "unsupported_file", "critical_quality_issue",
    }


def test_selective_regeneration_only_invalidates_downstream_outputs():
    invalidated, preserved = plan_selective_regeneration(
        {"script:1"},
        [
            RegenerationDependency("script:1", "scene:1"),
            RegenerationDependency("scene:1", "video:1"),
            RegenerationDependency("video:1", "subtitle:1"),
            RegenerationDependency("other:1", "video:2"),
        ],
        ["script:1", "scene:1", "video:1", "subtitle:1", "video:2"],
    )
    assert invalidated == ("scene:1", "script:1", "subtitle:1", "video:1")
    assert preserved == ("video:2",)


def test_token_bucket_rate_limit():
    bucket = TokenBucket(capacity=2, refill_per_second=1)
    assert bucket.allow(now=0)
    assert bucket.allow(now=0)
    assert not bucket.allow(now=0)
    assert bucket.allow(now=1)


def test_quota_decision():
    assert decide_quota(limit=10, consumed=7, requested=3).allowed
    assert not decide_quota(limit=10, consumed=7, requested=4).allowed


def test_storage_cleanup_preserves_referenced_and_final():
    now = __import__("datetime").datetime(2026, 10, 7, tzinfo=__import__("datetime").timezone.utc)
    objects = [
        StorageObject("old", 10, now - __import__("datetime").timedelta(days=31)),
        StorageObject("archive", 10, now - __import__("datetime").timedelta(days=20)),
        StorageObject("ref", 10, now - __import__("datetime").timedelta(days=40), referenced=True),
        StorageObject("final", 10, now - __import__("datetime").timedelta(days=40), final=True),
    ]
    archive, delete = plan_storage_cleanup(objects, policy=RetentionPolicy(), now=now)
    assert archive == ("archive",)
    assert delete == ("old",)


def test_storage_thresholds():
    assert storage_threshold(used_bytes=79, capacity_bytes=100) is None
    assert storage_threshold(used_bytes=80, capacity_bytes=100).name == "warning"
    assert storage_threshold(used_bytes=95, capacity_bytes=100).name == "emergency"


def test_alert_comparisons():
    assert evaluate_alert(AlertRule("latency", 2, "gte", "warning"), 2)
    assert not evaluate_alert(AlertRule("latency", 2, "gte", "warning"), 1)


def test_audit_redaction():
    assert redact_audit_metadata({"api_key": "secret", "provider": "groq"}) == {
        "api_key": "[REDACTED]",
        "provider": "groq",
    }


def test_legal_release_gate():
    assert legal_release_blockers({"terms": True, "privacy": True, "dpa": False, "dmca": False}) == ("dpa", "dmca")


def test_release_gate_and_e2e_gate():
    assert release_gate([
        __import__("app.services.code_completion", fromlist=["ReleaseEvidence"]).ReleaseEvidence("unit", automated=True),
        __import__("app.services.code_completion", fromlist=["ReleaseEvidence"]).ReleaseEvidence("legal", reserved=True),
    ])[0]
    ok, missing = __import__("app.services.code_completion", fromlist=["validate_e2e_evidence"]).validate_e2e_evidence(
        {"auth", "tenant_scope", "idea", "script", "asset_upload", "queue", "worker", "ffmpeg_whisper", "subtitle_review", "approval", "drive_export"}
    )
    assert ok and not missing
    assert len(DEFAULT_PRODUCTION_E2E) == 11
