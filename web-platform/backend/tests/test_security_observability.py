import pytest

from app.main import app
from client_utils import create_test_client


@pytest.mark.integration
@pytest.mark.security
def test_security_headers_are_present():
    with create_test_client(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "same-origin"
    assert "geolocation=()" in response.headers["permissions-policy"]


@pytest.mark.unit
@pytest.mark.security
def test_production_runtime_rejects_wildcard_cors():
    from app.core.config import Settings

    config = Settings(
        app_env="production",
        session_secret="x" * 64,
        session_cookie_secure=True,
        oauth_encryption_key="invalid",
        cors_origins="*",
        trusted_hosts="example.com",
        storage_provider="cloudinary",
        cloudinary_cloud_name="cloud",
        cloudinary_api_key="key",
        cloudinary_api_secret="secret",
        smtp_host="smtp.example.com",
        smtp_from_email="noreply@example.com",
    )
    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        config.validate_runtime()
