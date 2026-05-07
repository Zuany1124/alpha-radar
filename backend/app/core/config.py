from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://alpharadar:alpharadar@localhost:5432/alpharadar"
    redis_url: str = "redis://localhost:6379/0"
    helius_api_key: str = ""
    openai_api_key: str = ""
    scan_interval_minutes: int = 30
    signal_provider: str = "auto"
    signal_fixture_path: str = "tests/fixtures/solana_signal_fixture.json"
    signal_history_limit: int = 100
    signal_transfers_limit: int = 100
    signal_anomaly_threshold: float = 0.65
    default_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    default_analysis_model: str = "gpt-4.1-mini"
    evidence_fixture_path: str = "tests/fixtures/evidence_fixture.json"
    elasticsearch_url: str = ""
    elasticsearch_api_key: str = ""
    elasticsearch_evidence_index: str = "alpharadar-evidence"
    langsmith_api_key: str = ""
    langsmith_tracing: bool = False
    langsmith_project: str = "alpharadar-local"
    log_level: str = "INFO"
    environment: str = "local"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
