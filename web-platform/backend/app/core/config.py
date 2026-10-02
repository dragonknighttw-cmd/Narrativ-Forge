from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./narrativ_forge.db"
    bootstrap_admin_email: str = ""
    bootstrap_admin_password: str = ""
    session_secret: str = "development-only-change-this-secret"
    session_cookie_name: str = "nf_session"
    session_cookie_secure: bool = False
    session_ttl_seconds: int = 60 * 60 * 8
    cors_origins: str = "http://localhost:3000"
    trusted_hosts: str = "localhost,127.0.0.1"
    upload_dir: str = "./storage/uploads"
    max_upload_size_bytes: int = 52428800
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/drive/google/callback"
    oauth_encryption_key: str = ""
    ffmpeg_binary: str = "ffmpeg"
    whisper_command: str = "whisper"
    whisper_model: str = "small"
    processing_timeout_seconds: int = 3600

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def trusted_host_list(self) -> list[str]:
        return [item.strip() for item in self.trusted_hosts.split(",") if item.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    def validate_runtime(self) -> None:
        if not self.is_production:
            return
        if self.session_secret == "development-only-change-this-secret" or len(self.session_secret) < 32:
            raise RuntimeError("SESSION_SECRET must be a strong secret (32+ characters) in production")
        if self.dev_auth_password == "change-me":
            raise RuntimeError("DEV_AUTH_PASSWORD must be changed before production")
        if not self.session_cookie_secure:
            raise RuntimeError("SESSION_COOKIE_SECURE must be true in production")
        if not self.cors_origin_list:
            raise RuntimeError("CORS_ORIGINS must contain at least one allowed origin in production")
        if not self.trusted_host_list:
            raise RuntimeError("TRUSTED_HOSTS must contain at least one allowed host in production")
