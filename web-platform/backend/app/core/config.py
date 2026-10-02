from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./narrativ_forge.db"
    dev_auth_email: str = "admin@narrativ.local"
    dev_auth_password: str = "change-me"
    session_cookie_name: str = "nf_session"
    session_cookie_secure: bool = False
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "./storage/uploads"
    max_upload_size_bytes: int = 52428800
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/drive/google/callback"
    oauth_encryption_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()
