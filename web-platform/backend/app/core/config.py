from pydantic import Field, SecretStr
from cryptography.fernet import Fernet
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
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_storage_bucket: str = "narrativ-forge"
    supabase_signed_url_expiry_seconds: int = 900
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
    frontend_base_url: str = "http://localhost:3000"
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: SecretStr = SecretStr("")
    smtp_from_email: str = ""
    smtp_use_tls: bool = True
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_pro: str = ""
    stripe_price_business: str = ""
    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"
    whisper_command: str = "whisper"
    whisper_model: str = "small"
    processing_timeout_seconds: int = 3600
    processing_timeout_grace_seconds: int = 10
    worker_max_concurrency: int = Field(default=1, ge=1)
    single_user_mode: bool = False
    single_user_email: str = ""
    cloudflare_whisper_worker_url: str = ""
    cloudflare_whisper_shared_secret: str = ""
    cloudflare_whisper_token_ttl_seconds: int = 300
    cloudflare_whisper_daily_neuron_budget: int = 10000
    cloudflare_whisper_warning_threshold: float = 0.80
    cloudflare_whisper_fallback_threshold: float = 0.95
    whisper_remote_timeout_seconds: float = Field(default=60.0, ge=5, le=300)
    whisper_remote_enabled: bool = True
    cloudflare_whisper_neurons_per_audio_minute: float = 41.14
    # Provider budgets are planning defaults until live account limits are verified.
    agnes_daily_seconds_budget: int = Field(default=500, ge=0)
    groq_daily_requests_budget: int = Field(default=1000, ge=0)
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.3-70b-versatile"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    # Free-only OpenRouter routing. The runtime rejects model IDs that are not explicitly free.
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_models: str = "google/gemma-4-31b-it:free,cohere/north-mini-code:free,nvidia/nemotron-3-super-120b-a12b:free,liquid/lfm-2.5-2.6b:free"
    ai_provider_timeout_seconds: float = Field(default=45.0, ge=1, le=300)
    provider_quota_warning_threshold: float = Field(default=0.80, ge=0, le=1)
    provider_quota_fallback_threshold: float = Field(default=0.95, ge=0, le=1)

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
        if self.single_user_mode and not self.single_user_email:
            raise RuntimeError("SINGLE_USER_EMAIL must be configured when SINGLE_USER_MODE is enabled")
        if not self.session_secret or len(self.session_secret) < 32 or self.session_secret in {"change-me", "change-me-in-production", "dev-secret", "secret"}:
            raise RuntimeError("SESSION_SECRET must be a strong non-default secret (32+ characters) in production")
        if not self.session_cookie_secure:
            raise RuntimeError("SESSION_COOKIE_SECURE must be true in production")
        if not self.oauth_encryption_key:
            raise RuntimeError("OAUTH_ENCRYPTION_KEY must be configured in production")
        try:
            Fernet(self.oauth_encryption_key.encode())
        except Exception as exc:
            raise RuntimeError("OAUTH_ENCRYPTION_KEY must be a valid Fernet key in production") from exc
        if not self.single_user_mode and (not self.smtp_host or not self.smtp_from_email):
            raise RuntimeError("SMTP_HOST and SMTP_FROM_EMAIL must be configured in production unless SINGLE_USER_MODE is enabled")
        if not self.cors_origin_list:
            raise RuntimeError("CORS_ORIGINS must contain at least one allowed origin in production")
        if any(origin == "*" for origin in self.cors_origin_list):
            raise RuntimeError("CORS_ORIGINS must not use wildcard in production")
        if not self.trusted_host_list:
            raise RuntimeError("TRUSTED_HOSTS must contain at least one allowed host in production")
        if "*" in self.trusted_host_list:
            raise RuntimeError("TRUSTED_HOSTS must not use wildcard in production")
        if self.storage_provider.lower() not in {"cloudinary", "b2", "hybrid"}:
            raise RuntimeError("STORAGE_PROVIDER must be one of: cloudinary, b2, hybrid in production")
        if self.storage_provider.lower() == "hybrid":
            required = {
                "CLOUDINARY_CLOUD_NAME": self.cloudinary_cloud_name,
                "CLOUDINARY_API_KEY": self.cloudinary_api_key,
                "CLOUDINARY_API_SECRET": self.cloudinary_api_secret,
                "B2_APPLICATION_KEY_ID": self.b2_application_key_id,
                "B2_APPLICATION_KEY": self.b2_application_key,
                "B2_BUCKET_NAME": self.b2_bucket_name,
                "B2_REGION": self.b2_region,
                "SUPABASE_URL": self.supabase_url,
                "SUPABASE_SERVICE_ROLE_KEY": self.supabase_service_role_key,
                "SUPABASE_STORAGE_BUCKET": self.supabase_storage_bucket,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise RuntimeError("Hybrid storage configuration missing: " + ", ".join(missing))
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
