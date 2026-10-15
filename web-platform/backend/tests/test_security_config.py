import pytest
from cryptography.fernet import Fernet

from app.core.config import Settings, settings
from app.main import app


pytestmark = [pytest.mark.unit, pytest.mark.security]


def test_settings_instance_is_exported_and_application_imports():
    assert isinstance(settings, Settings)
    assert app.title == "Narrativ Forge API"


def production_settings(**overrides) -> Settings:
    values = {
        "app_env": "production",
        "database_url": "sqlite:///./test.db",
        "cors_origins": "https://app.example.com",
        "trusted_hosts": "api.example.com",
        "session_cookie_secure": True,
        "storage_provider": "b2",
        "b2_application_key_id": "key-id",
        "b2_application_key": "key-secret",
        "b2_bucket_name": "bucket",
        "b2_region": "us-west-002",
        "oauth_encryption_key": Fernet.generate_key().decode(),
        "smtp_host": "smtp.example.com",
        "smtp_from_email": "noreply@example.com",
        "supabase_url": "https://project.supabase.co",
        "supabase_anon_key": "sb_publishable_test_key",
        "supabase_owner_user_id": "000afedc-2811-4a4e-9ea0-7d24218c44f2",
        "supabase_owner_email": "dragonknight.tw@gmail.com",
    }
    values.update(overrides)
    return Settings(**values)


def test_production_rejects_missing_session_secret():
    settings = production_settings(session_secret="")
    try:
        settings.validate_runtime()
    except RuntimeError as exc:
        assert "SESSION_SECRET" in str(exc)
    else:
        raise AssertionError("production must reject a missing session secret")


def test_production_rejects_short_session_secret():
    settings = production_settings(session_secret="x" * 31)
    try:
        settings.validate_runtime()
    except RuntimeError as exc:
        assert "SESSION_SECRET" in str(exc)
    else:
        raise AssertionError("production must reject a short session secret")


def test_production_accepts_strong_session_secret():
    settings = production_settings(session_secret="x" * 32)
    settings.validate_runtime()
