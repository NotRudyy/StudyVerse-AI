from functools import lru_cache
from pydantic import Field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "StudyVerse AI API"
    demo_mode: bool = True
    database_url: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"
    use_vertex_ai: bool = False
    google_cloud_location: str = "us-central1"
    google_cloud_project: str | None = None
    gcs_bucket: str | None = None
    jwt_secret: str = "local-demo-only-change-this-secret-before-deploy"
    upload_dir: str = "uploads"
    max_upload_bytes: int = 20 * 1024 * 1024
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"])
    gemini_embedding_model: str = "gemini-embedding-001"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
