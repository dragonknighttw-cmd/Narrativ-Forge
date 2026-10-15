import pytest

from app.services.expanded_production import (
    BatchPlan,
    CalendarEntry,
    ContentVersion,
    HookCandidate,
    SeoMetadata,
    StorySplitPlan,
    ThumbnailCandidate,
    TranslationRequest,
    UploadSession,
    UploadState,
    WatermarkPolicy,
    check_continuity,
    evaluate_watermark_policy,
    next_version_number,
    rank_hook_candidates,
    retained_versions,
    select_thumbnail_candidates,
    validate_batch_plan,
    validate_calendar,
    validate_seo,
    validate_story_split_plan,
    validate_translation,
)


pytestmark = pytest.mark.unit


def test_resumable_upload_resume_and_checksum():
    session = UploadSession("u1", "a.txt", 6)
    assert session.accept_chunk(offset=0, data=b"abc") == 3
    assert session.accept_chunk(offset=3, data=b"def") == 6
    checksum = session.finalize()
    assert checksum
    assert session.state is UploadState.COMPLETE


def test_resumable_upload_rejects_wrong_offset_and_overflow():
    session = UploadSession("u1", "a.txt", 3)
    with pytest.raises(ValueError, match="offset_mismatch"):
        session.accept_chunk(offset=1, data=b"a")
    with pytest.raises(ValueError, match="upload_exceeds_declared_size"):
        session.accept_chunk(offset=0, data=b"abcd")


def test_version_retention_preserves_final_and_recent():
    versions = [
        ContentVersion(f"v{i}", "ep", i, "script", is_final=(i == 1))
        for i in range(1, 6)
    ]
    assert next_version_number(versions) == 6
    kept = retained_versions(versions, keep_last=3)
    assert {item.number for item in kept} == {1, 3, 4, 5}


def test_story_hook_seo_and_thumbnail_contracts():
    assert validate_story_split_plan(StorySplitPlan(1, "Ep 1", 180, ("s1",), ("c1",), "next")) == []
    ranked = rank_hook_candidates([
        HookCandidate("a", "warning", 50),
        HookCandidate("b", "mystery", 80),
        HookCandidate("c", "number", 70),
        HookCandidate("d", "shock", 90),
    ])
    assert [item.text for item in ranked] == ["d", "b", "c"]
    assert validate_seo(SeoMetadata("Title", "Caption", ("kw",), ("#x",))) == []
    assert [x.asset_key for x in select_thumbnail_candidates([
        ThumbnailCandidate("b", 80, "face"),
        ThumbnailCandidate("a", 90, "hook"),
    ])] == ["a", "b"]


def test_continuity_calendar_batch_translation_and_watermark():
    issues = check_continuity(
        expected_characters={"A"}, actual_characters={"A", "B"},
        expected_locations={"home"}, actual_locations={"home", "street"},
    )
    assert {item.message for item in issues} == {"unexpected_character:B", "unexpected_location:street"}
    assert validate_calendar([
        CalendarEntry("e1", "2026-10-07", "10:00"),
        CalendarEntry("e2", "2026-10-07", "10:00"),
    ])
    assert validate_batch_plan(BatchPlan(("e1",), False, 5)) == ["human_approval_required"]
    assert validate_translation(TranslationRequest("my", "en", "မင်္ဂလာပါ")) == []
    assert evaluate_watermark_policy(
        provider="candidate", watermark_present=True,
        policy=WatermarkPolicy(commercial_use=True, watermark_free_required=True),
    )


def test_upload_finalize_detects_checksum_mismatch():
    session = UploadSession("u1", "a.txt", 3)
    session.accept_chunk(offset=0, data=b"abc")
    with pytest.raises(ValueError, match="checksum_mismatch"):
        session.finalize("00" * 32)
