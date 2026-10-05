import pytest

from app.services.storage import SupabaseStorageProvider, storage_provider_for_asset


@pytest.mark.unit
def test_storage_provider_routes_media_and_small_assets():
    assert storage_provider_for_asset("video", 1_000, "video/mp4") == "b2"
    assert storage_provider_for_asset("audio", 1_000, "audio/wav") == "b2"
    assert storage_provider_for_asset("thumbnail", 1_000, "image/jpeg") == "cloudinary"
    assert storage_provider_for_asset("srt", 1_000, "text/plain") == "supabase"
    assert storage_provider_for_asset("binary", 51 * 1024 * 1024, "application/octet-stream") == "b2"


@pytest.mark.unit
def test_supabase_object_endpoint_does_not_insert_empty_action_segment():
    provider = object.__new__(SupabaseStorageProvider)
    provider.url = "https://example.supabase.co"
    provider.bucket = "narrativ-forge"

    assert provider._url("") == "https://example.supabase.co/storage/v1/object/narrativ-forge"
    assert provider._url("", "episodes/ep-1/test.srt") == (
        "https://example.supabase.co/storage/v1/object/narrativ-forge/episodes/ep-1/test.srt"
    )
