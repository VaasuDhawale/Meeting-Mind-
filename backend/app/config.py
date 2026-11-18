"""
Application configuration.

All settings are loaded from environment variables (or .env file).
Pydantic BaseSettings provides validation and type coercion.
"""

from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "MeetingMind"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-to-a-random-64-char-string-in-production"

    # --- Backend ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> list[str]:
        """Support comma-separated strings or JSON arrays in BACKEND_CORS_ORIGINS."""
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, set, tuple)):
            return list(v)
        return v

    # --- Database ---
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR.as_posix()}/meetingmind.db"

    # --- Storage Directories ---
    storage_dir: str = str(BASE_DIR / "storage")
    upload_dir: str = str(BASE_DIR / "storage" / "uploads")
    keyframes_dir: str = str(BASE_DIR / "storage" / "keyframes")
    reports_dir: str = str(BASE_DIR / "storage" / "reports")
    demo_dir: str = str(BASE_DIR / "demo_data")

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # --- MinIO ---
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket_name: str = "meetingmind"
    minio_use_ssl: bool = False

    # --- JWT ---
    jwt_secret_key: str = "change-me-to-a-different-random-64-char-string"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # --- AI Services ---
    openai_api_key: str = ""
    assemblyai_api_key: str = ""
    google_ai_api_key: str = ""

    # --- File Upload Limits ---
    max_video_size_mb: int = 500
    max_document_size_mb: int = 50
    allowed_video_extensions: list[str] = [".mp4", ".webm", ".mkv", ".avi", ".mov"]
    allowed_audio_extensions: list[str] = [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"]
    allowed_document_extensions: list[str] = [".pdf", ".pptx", ".ppt", ".txt", ".docx"]

    # --- Processing ---
    media_retention_days: int = 7

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


# Singleton settings instance
settings = Settings()
