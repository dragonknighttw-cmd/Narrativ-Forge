import pytest

from app.services.provider_registry import DEFAULT_CAPABILITIES, ProviderRegistry, ProviderSpec


def test_provider_registry_orders_by_priority_and_filters_disabled():
    registry = ProviderRegistry()
    registry.register(ProviderSpec("backup", "video", lambda: "b", priority=20))
    registry.register(ProviderSpec("primary", "video", lambda: "p", priority=10))
    registry.register(ProviderSpec("disabled", "video", lambda: "x", priority=1, enabled=False))
    assert [item.name for item in registry.require("video")] == ["primary", "backup"]


def test_provider_registry_reports_missing_capability():
    registry = ProviderRegistry()
    with pytest.raises(LookupError):
        registry.require("unknown")
    assert "cloudflare_whisper" in DEFAULT_CAPABILITIES["transcription"]
