import pytest

from app.services.storage import storage_provider_for_asset


@pytest.mark.unit
@pytest.mark.parametrize(
    ("asset_type", "size_bytes", "content_type", "expected"),
    [
        ("video", 8 * 1024 * 1024, "video/mp4", "b2"),
        ("audio", 2 * 1024 * 1024, "audio/mpeg", "b2"),
        ("thumbnail", 9 * 1024 * 1024, "image/webp", "cloudinary"),
        ("cover", 10 * 1024 * 1024, "image/png", "cloudinary"),
        ("thumbnail", 11 * 1024 * 1024, "image/png", "supabase"),
        ("srt", 2 * 1024 * 1024, "text/plain", "supabase"),
        ("manifest", 49 * 1024 * 1024, "application/json", "supabase"),
        ("image", 60 * 1024 * 1024, "image/png", "b2"),
    ],
)
def test_hybrid_storage_routing(asset_type, size_bytes, content_type, expected, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "storage_provider", "hybrid")
    assert storage_provider_for_asset(asset_type, size_bytes, content_type) == expected


def test_media_mime_type_overrides_generic_asset_type(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "storage_provider", "hybrid")
    assert storage_provider_for_asset("asset", 1 * 1024 * 1024, "video/mp4") == "b2"
    assert storage_provider_for_asset("asset", 1 * 1024 * 1024, "audio/mpeg") == "b2"
