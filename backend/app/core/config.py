from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Lexis API"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"
    frontend_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:55433/lexis"
    session_cookie_name: str = "lexis_session"
    session_max_age_seconds: int = 60 * 60 * 24 * 14
    session_cookie_secure: bool = False
    secret_encryption_key: SecretStr | None = None
    llm_provider: Literal["mock", "openrouter"] = "mock"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_api_key: SecretStr | None = None
    openrouter_model: str | None = None
    openrouter_http_referer: str | None = "http://localhost:5173"
    openrouter_app_title: str | None = "Lexis"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
