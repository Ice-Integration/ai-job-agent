from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://jobagent:jobagent@localhost:5432/jobagent"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-luna"
    embedding_model: str = "text-embedding-3-small"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    max_upload_bytes: int = 5_000_000
    job_search_limit: int = 50
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    auth_bootstrap_email: str = ""
    auth_bootstrap_password: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
