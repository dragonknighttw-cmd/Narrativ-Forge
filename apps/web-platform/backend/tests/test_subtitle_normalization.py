import unicodedata

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.services.subtitles import (
    UnsupportedTextFormatError,
    normalize_burmese_text,
    normalization_contract,
    zawgyi_probability,
)

pytestmark = pytest.mark.unit


def test_unicode_burmese_is_nfc_normalized_and_contract_is_explicit():
    source = "\u1025\u102e"
    normalized, metadata = normalize_burmese_text(source)
    assert normalized == unicodedata.normalize("NFC", source) == "ဦ"
    assert metadata["mode"] == "unicode_nfc_only"
    assert metadata["unicode_normalization"] == "NFC"
    assert metadata["zawgyi_conversion_supported"] is False
    assert metadata["zawgyi_detected"] is None
    assert metadata["zawgyi_probability"] is None
    assert normalization_contract() == {
        "mode": "unicode_nfc_only",
        "unicode_normalization": "NFC",
        "zawgyi_conversion_supported": False,
    }


def test_unicode_burmese_is_preserved():
    source = "မြန်မာစာ"
    normalized, metadata = normalize_burmese_text(source)
    assert normalized == source
    assert metadata["changed"] is False


def test_legacy_zawgyi_conversion_is_explicitly_unsupported():
    source = "မ္း"
    normalized, metadata = normalize_burmese_text(source)
    assert normalized == unicodedata.normalize("NFC", source)
    assert normalized == source
    assert metadata["zawgyi_conversion_supported"] is False
    with pytest.raises(UnsupportedTextFormatError, match="Zawgyi detection and conversion are unsupported"):
        zawgyi_probability(source)
    with pytest.raises(UnsupportedTextFormatError, match="thresholds are unsupported"):
        normalize_burmese_text(source, zawgyi_threshold=0.8)


def test_normalization_mode_cannot_enable_zawgyi():
    with pytest.raises(ValidationError):
        Settings(subtitle_normalization_mode="zawgyi")
