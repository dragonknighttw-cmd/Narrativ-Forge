import pytest

pytestmark = pytest.mark.unit

from app.services.phase_69_76 import (
    ChaosDrill, DependencyLicense, EvidencePack, PrivacyRequest,
    RestoreVerification, RolloutPolicy, SchemaDrift, SecretRequirement,
    validate_release_operations,
)


def test_rollout_schema_and_restore_contracts():
    assert RolloutPolicy("new-editor", ("internal", "beta"), 25).valid()
    drift = SchemaDrift("episodes", ("id", "title"), ("id", "title", "status"))
    assert drift.missing == ()
    assert drift.unexpected == ("status",)
    assert drift.compatible()
    assert RestoreVerification("backup-1", "restore-1", True, "head-7", "head-7").verified()


def test_privacy_secrets_and_license_contracts():
    assert PrivacyRequest("subject-1", "erasure", "consent-withdrawal", True, "evidence-1").closed()
    assert SecretRequirement("STRIPE_SECRET_KEY", True, True, "secret-manager").ready()
    assert not SecretRequirement("STRIPE_SECRET_KEY", True, False).ready()
    assert DependencyLicense("pkg", "1.0", "MIT", True).valid()


def test_chaos_and_evidence_pack_are_deterministic():
    assert ChaosDrill("worker-loss", 120, 90, True).passed()
    pack = EvidencePack("a" * 40, ("z", "a"))
    assert pack.ready()
    assert pack.fingerprint == EvidencePack("a" * 40, ("a", "z")).fingerprint


def test_release_operations_aggregate_blocks():
    errors = validate_release_operations(
        RolloutPolicy("f", ("internal",), 10),
        SchemaDrift("t", ("id",), ("id",)),
        RestoreVerification("b", "r", True, "h", "h"),
        PrivacyRequest("s", "access", "basis", True, "e"),
        (SecretRequirement("A", True, True, "vault"),),
        (DependencyLicense("pkg", "1", "MIT", True),),
        ChaosDrill("restore", 10, 5, True),
        EvidencePack("a" * 40, ("e",)),
    )
    assert errors == []


def test_blocked_inputs_are_explicit():
    errors = validate_release_operations(
        RolloutPolicy("f", ("internal",), 10),
        SchemaDrift("t", ("id", "missing"), ("id",)),
        RestoreVerification("b", "r", False, "h1", "h2"),
        PrivacyRequest("s", "erasure", "basis", False),
        (SecretRequirement("A", True, False),),
        (DependencyLicense("pkg", "1", "GPL", False),),
        ChaosDrill("restore", 10, None, False),
        EvidencePack("a" * 40, ()),
    )
    assert set(errors) == {"schema_drift", "restore_unverified", "privacy_request_open", "secret_requirements_unready", "license_blocked", "chaos_drill_failed", "evidence_pack_blocked"}
