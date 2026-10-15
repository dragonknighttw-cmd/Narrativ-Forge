import pytest

pytestmark = pytest.mark.unit

from app.services.content_quality import assess_content
from app.services.series_continuity import build_series_bible, check_continuity


def test_content_quality_detects_short_and_pacing_problems():
    report = assess_content("too short", [60], target_seconds=180)
    assert report.score < 100
    assert "script_too_short" in report.issues
    assert report.pacing_ok is False


def test_series_bible_deduplicates_and_checks_recurring_elements():
    bible = build_series_bible(
        "Series A",
        "Premise",
        recurring_elements=["hero", "hero", "location"],
        continuity_rules=["rule"],
    )
    assert bible.recurring_elements == ("hero", "location")
    issues = check_continuity(
        bible,
        title="Series A — Episode 1",
        synopsis="The hero returns.",
    )
    assert any(issue.field == "recurring_element" and "location" in issue.message for issue in issues)
