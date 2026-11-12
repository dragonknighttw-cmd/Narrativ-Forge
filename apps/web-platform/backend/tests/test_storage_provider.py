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
        oauth_encryption_key=__import__("cryptography.fernet", fromlist=["Fernet"]).Fernet.generate_key().decode(),
        storage_provider="storj",
        smtp_host="smtp.example.com",
        smtp_from_email="noreply@example.com",
    )
    with pytest.raises(RuntimeError, match="STORAGE_PROVIDER must be one of"):
        settings.validate_runtime()


@pytest.mark.unit
def test_cloudinary_assets_use_authenticated_delivery(monkeypatch, tmp_path):
    import sys
    import types
    from unittest.mock import Mock

    from app.core.config import settings
    from app.services.storage import CloudinaryStorageProvider

    cloudinary = types.ModuleType("cloudinary")
    cloudinary.__path__ = []
    cloudinary.config = Mock()
    uploader = types.ModuleType("cloudinary.uploader")
    uploader.upload = Mock(return_value={"public_id": "episodes/test"})
    uploader.upload_large = Mock(return_value={"public_id": "episodes/test"})
    uploader.destroy = Mock(return_value={"result": "ok"})
    utils = types.ModuleType("cloudinary.utils")
    utils.cloudinary_url = Mock(return_value=("https://res.cloudinary.com/signed/authenticated", {}))
    cloudinary.api = types.SimpleNamespace(resource=Mock(return_value={"public_id": "episodes/test"}))
    cloudinary.uploader = uploader
    cloudinary.utils = utils

    monkeypatch.setitem(sys.modules, "cloudinary", cloudinary)
    monkeypatch.setitem(sys.modules, "cloudinary.uploader", uploader)
    monkeypatch.setitem(sys.modules, "cloudinary.utils", utils)
    monkeypatch.setattr(settings, "cloudinary_cloud_name", "test-cloud")
    monkeypatch.setattr(settings, "cloudinary_api_key", "test-key")
    monkeypatch.setattr(settings, "cloudinary_api_secret", "test-secret")

    provider = CloudinaryStorageProvider()
    source = tmp_path / "thumbnail.png"
    source.write_bytes(b"private-narrativ-asset")
    provider.upload_file(source, "episodes/test/assets/thumbnail.png", "image/png")

    assert uploader.upload.call_args.kwargs["type"] == "authenticated"
    assert provider.download_url("episodes/test/assets/thumbnail.png").startswith("https://")
    assert utils.cloudinary_url.call_args.kwargs["type"] == "authenticated"
    assert provider.exists("episodes/test/assets/thumbnail.png") is True
    assert cloudinary.api.resource.call_args.kwargs["type"] == "authenticated"
    provider.delete("episodes/test/assets/thumbnail.png")
    assert uploader.destroy.call_args.kwargs["type"] == "authenticated"
