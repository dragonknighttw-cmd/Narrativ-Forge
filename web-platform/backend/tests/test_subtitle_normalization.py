from app.services.subtitles import normalize_burmese_text, zawgyi_probability


def test_zawgyi_is_detected_and_normalized():
    source = "မ္း"
    normalized, metadata = normalize_burmese_text(source)
    assert metadata["zawgyi_detected"] is True
    assert zawgyi_probability(source) >= 0.8
    assert normalized == "မ်း"
    assert normalized != source


def test_unicode_burmese_is_left_in_unicode_form():
    source = "မြန်မာစာ"
    normalized, metadata = normalize_burmese_text(source)
    assert metadata["zawgyi_detected"] is False
    assert normalized == source
