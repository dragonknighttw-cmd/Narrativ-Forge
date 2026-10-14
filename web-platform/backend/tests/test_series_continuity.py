import pytest

from app.services.series_continuity import build_series_bible, check_continuity

pytestmark = pytest.mark.unit


def test_build_series_bible_normalizes_and_deduplicates_fields():
    bible = build_series_bible(
        "  ပုဂံ  သမိုင်း  ",
        "  မြန်မာ့ ရှေးဟောင်း အမွေအနှစ်  ",
        tone="  Curious   and warm ",
        audience=" Burmese learners ",
        recurring_elements=["ဇေယျာ", " ပုဂံ ", "ဇေယျာ", ""],
        continuity_rules=["Unicode only", " Unicode only ", "Keep the narrator curious"],
    )

    assert bible.title == "ပုဂံ သမိုင်း"
    assert bible.premise == "မြန်မာ့ ရှေးဟောင်း အမွေအနှစ်"
    assert bible.tone == "Curious and warm"
    assert bible.audience == "Burmese learners"
    assert bible.recurring_elements == ("ဇေယျာ", "ပုဂံ")
    assert bible.continuity_rules == ("Unicode only", "Keep the narrator curious")


def test_check_continuity_accepts_series_identity_and_recurring_elements():
    bible = build_series_bible(
        "ပုဂံ သမိုင်း",
        "ပုဂံမြို့အကြောင်း",
        recurring_elements=["ဇေယျာ", "ရွှေစည်းခုံ"],
    )

    issues = check_continuity(
        bible,
        title="ပုဂံ သမိုင်း — ဇေယျာ၏ ခရီးစဉ်",
        synopsis="ဇေယျာသည် ရွှေစည်းခုံကို လေ့လာသည်။",
    )

    assert issues == []


def test_check_continuity_reports_missing_series_identity_and_recurring_elements():
    bible = build_series_bible(
        "ပုဂံ သမိုင်း",
        "ပုဂံမြို့အကြောင်း",
        recurring_elements=["ဇေယျာ", "ရွှေစည်းခုံ"],
    )

    issues = check_continuity(
        bible,
        title="မိုးရာသီ ခရီးစဉ်",
        synopsis="မိတ်ဆွေများ မြို့ပြင်သို့ ခရီးထွက်ကြသည်။",
    )

    assert [issue.field for issue in issues] == [
        "series_title",
        "recurring_element",
        "recurring_element",
    ]
    assert "Missing recurring element: ဇေယျာ" in [issue.message for issue in issues]
    assert "Missing recurring element: ရွှေစည်းခုံ" in [issue.message for issue in issues]
