"""Application configuration.

All runtime configuration is read from environment variables (or a local .env
file) via pydantic-settings. Nothing that varies between environments —
credentials, model names, database URLs — should be hard-coded anywhere else in
the codebase; it belongs here.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ directory — anchors .env discovery (and relative SQLite paths) so
# the server behaves identically no matter which directory it starts from.
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application
    app_name: str = "TeachBack"
    env: str = "development"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Database
    database_url: str = "sqlite:///./teachback.db"

    # LLM provider ("sarvam" | "mock")
    llm_provider: str = "mock"
    llm_api_key: str = ""
    llm_model: str = "sarvam-m"
    llm_base_url: str = "https://api.sarvam.ai"

    # Speech-to-text provider ("sarvam" | "mock")
    stt_provider: str = "mock"
    stt_api_key: str = ""
    stt_model: str = "saarika:v2"

    # Embeddings / retrieval
    embedding_provider: str = "mock"
    retriever_backend: str = "local"  # "local" | "qdrant"
    qdrant_url: str = ""
    qdrant_api_key: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
