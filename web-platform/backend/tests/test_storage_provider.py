import pytest

from app.core.config import Settings
from app.services.storage import B2StorageProvider, S3CompatibleStorageProvider, get_storage


@pytest.mark.unit
def test_b2_provider_is_s3_compatible_adapter():
    assert issubclass(B2StorageProvider, S3CompatibleStorageProvider)
    assert get_storage.__name__ == "get_storage"


@pytest.mark.unit
def test_production_requires_supported_hybrid_storage():
    settings = Settings(
        app_env="production",
        database_url="sqlite:///./gate.db",
        session_secret="x" * 40,
        session_cookie_secure=True,
        cors_origins="https://app.example.com",
        trusted_hosts="api.example.com",
        oauth_encryption_key="y" * 32,
        storage_provider="storj",
    )
    with pytest.raises(RuntimeError, match="STORAGE_PROVIDER must be one of"):
        settings.validate_runtime()
