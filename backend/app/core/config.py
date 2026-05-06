from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://alpharadar:alpharadar@localhost:5432/alpharadar"
    redis_url: str = "redis://localhost:6379/0"
    helius_api_key: str = ""
    openai_api_key: str = ""
    scan_interval_minutes: int = 30
    default_embedding_model: str = "text-embedding-3-small"
    default_analysis_model: str = "gpt-4.1-mini"
    langsmith_api_key: str = ""
    langsmith_tracing: bool = False
    langsmith_project: str = "alpharadar-local"
    log_level: str = "INFO"
    environment: str = "local"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
