import pytest

pytestmark = pytest.mark.unit

from app.services.phase_52_60 import (
    ArchiveRecord,
    AudioCue,
    AudioTrack,
    ConsistencyProfile,
    ManualValidation,
    SocialAnalyticsEvent,
    ThumbnailCandidate,
    TrailerPlan,
    TranslationTerm,
    UIStateAudit,
    normalize_subtitle_text,
    select_thumbnail_shortlist,
    validate_next_phase_inputs,
)


def test_trailer_and_translation_contracts():
    assert TrailerPlan("series-1", 60, ("hook", "turn", "payoff"), "first-second hook").valid()
    assert TranslationTerm("Hello", "မင်္ဂလာပါ", "my", "glossary-v1").valid()
    assert normalize_subtitle_text("  one\t two\n\n\nthree  ") == "one two\n\nthree"


def test_audio_cues_and_rights_are_validated():
    cue = AudioCue("bgm-1", 0, 5000, -3, 6)
    assert cue.valid()
    assert AudioTrack("bgm-1", "license-1", -14, (cue,)).valid()
    assert not AudioCue("bgm-1", 5, 5).valid()


def test_thumbnail_selection_is_deterministic_and_caps_at_five():
    candidates = tuple(
        ThumbnailCandidate(f"c{i}", f"asset-{i}", score=i / 10, rank=i)
        for i in range(1, 11)
    )
    shortlist = select_thumbnail_shortlist(candidates)
    assert len(shortlist) == 5
    assert [c.candidate_id for c in shortlist] == ["c10", "c9", "c8", "c7", "c6"]


def test_consistency_social_archive_and_manual_contracts():
    profile = ConsistencyProfile("p1", "model-v1", ("character-1",), "accepted")
    event = SocialAnalyticsEvent("youtube", "evt-7", "retention", 0.81, "2026-10-08T01:00:00Z")
    archive = ArchiveRecord("asset-1", "cold", False, True, "2027-01-01")
    manual = ManualValidation("episode-1", ("evidence-1", "evidence-2"), 93.5, ("subtitle-wrap",), True)
    assert profile.valid()
    assert event.valid()
    assert event.idempotency_key() == "youtube:evt-7"
    assert archive.purge_allowed()
    assert manual.valid()


def test_archive_legal_hold_and_ui_audit_block_completion():
    held = ArchiveRecord("asset-1", "cold", True, True, "2027-01-01")
    assert not held.purge_allowed()
    incomplete = UIStateAudit("series", ("loading", "error"), False, False)
    assert not incomplete.complete()


def test_all_next_phase_contracts_can_be_validated_together():
    errors = validate_next_phase_inputs(
        TrailerPlan("series", 45, ("hook", "payoff"), "hook"),
        TranslationTerm("a", "က", "my", "v1"),
        AudioTrack("bgm", "rights-1", -14, (AudioCue("bgm", 0, 1000),)),
        ConsistencyProfile("p", "m1", ("id",)),
        SocialAnalyticsEvent("platform", "1", "views", 10, "2026-10-08T00:00:00Z"),
        ArchiveRecord("a", "cold", False, True, "2027-01-01"),
        ManualValidation("ep", ("e1",), 10),
        UIStateAudit("route", ("loading", "empty", "error", "success"), True, True, "ui-1"),
    )
    assert errors == []
