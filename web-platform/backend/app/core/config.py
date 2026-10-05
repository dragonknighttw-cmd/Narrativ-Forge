from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./narrativ_forge.db"
    redis_url: str | None = None
    bootstrap_admin_email: str = ""
    bootstrap_admin_password: str = ""
    session_secret: str = ""
    sentry_dsn: SecretStr = SecretStr("")
    session_cookie_name: str = "nf_session"
    session_cookie_secure: bool = False
    session_ttl_seconds: int = 60 * 60 * 8
    cors_origins: str = "http://localhost:3000"
    trusted_hosts: str = "localhost,127.0.0.1"
    upload_dir: str = "./storage/uploads"
    max_upload_size_bytes: int = 52428800
    upload_chunk_size_bytes: int = Field(default=8 * 1024 * 1024, ge=5 * 1024 * 1024, le=5 * 1024 * 1024 * 1024)
    upload_session_ttl_seconds: int = Field(default=86400, ge=3600, le=604800)
    idempotency_ttl_seconds: int = Field(default=86400, ge=60, le=2592000)
    storage_provider: str = "local"
    storage_replica_provider: str = ""
    storage_replica_enabled: bool = False
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""
    cloudinary_folder: str = "narrativ-forge"
    cloudinary_chunk_size_bytes: int = Field(default=20 * 1024 * 1024, ge=5 * 1024 * 1024, le=100 * 1024 * 1024)
    asset_retention_days: int = 30
    temp_file_retention_hours: int = 24
    # Legacy B2 settings remain readable for data migration/legacy asset access.
    b2_application_key_id: str = ""
    b2_application_key: str = ""
    b2_bucket_name: str = ""
    b2_region: str = ""
    b2_endpoint_url: str = ""
    b2_signed_url_expiry_seconds: int = 900
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/drive/google/callback"
    oauth_encryption_key: str = ""
    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"
    whisper_command: str = "whisper"
    whisper_model: str = "small"
    processing_timeout_seconds: int = 3600
    processing_timeout_grace_seconds: int = 10
    worker_max_concurrency: int = Field(default=1, ge=1)

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
        if not self.session_secret or len(self.session_secret) < 32:
            raise RuntimeError("SESSION_SECRET must be a strong secret (32+ characters) in production")
        if not self.session_cookie_secure:
            raise RuntimeError("SESSION_COOKIE_SECURE must be true in production")
        if not self.cors_origin_list:
            raise RuntimeError("CORS_ORIGINS must contain at least one allowed origin in production")
        if not self.trusted_host_list:
            raise RuntimeError("TRUSTED_HOSTS must contain at least one allowed host in production")
        if self.storage_provider.lower() not in {"cloudinary", "b2"}:
            raise RuntimeError("STORAGE_PROVIDER must be one of: cloudinary, b2 in production")
        if self.storage_provider.lower() == "cloudinary":
            required = {
                "CLOUDINARY_CLOUD_NAME": self.cloudinary_cloud_name,
                "CLOUDINARY_API_KEY": self.cloudinary_api_key,
                "CLOUDINARY_API_SECRET": self.cloudinary_api_secret,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise RuntimeError("Cloudinary storage configuration missing: " + ", ".join(missing))
        if self.storage_replica_enabled and self.storage_replica_provider.lower() not in {"cloudinary", "b2"}:
            raise RuntimeError("STORAGE_REPLICA_PROVIDER must be one of: cloudinary, b2 when replication is enabled")
        if self.storage_replica_enabled and self.storage_replica_provider.lower() == self.storage_provider.lower():
            raise RuntimeError("STORAGE_REPLICA_PROVIDER must differ from STORAGE_PROVIDER")
        if self.storage_replica_enabled and self.storage_replica_provider.lower() == "cloudinary":
            required = {
                "CLOUDINARY_CLOUD_NAME": self.cloudinary_cloud_name,
                "CLOUDINARY_API_KEY": self.cloudinary_api_key,
                "CLOUDINARY_API_SECRET": self.cloudinary_api_secret,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise RuntimeError("Cloudinary replica configuration missing: " + ", ".join(missing))
        if self.storage_provider.lower() == "b2":
            required = {
                "B2_APPLICATION_KEY_ID": self.b2_application_key_id,
                "B2_APPLICATION_KEY": self.b2_application_key,
                "B2_BUCKET_NAME": self.b2_bucket_name,
                "B2_REGION": self.b2_region,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise RuntimeError("B2 storage configuration missing: " + ", ".join(missing))


settings = Settings()
