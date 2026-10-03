from app.core.config import Settings, settings
from app.main import app


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
