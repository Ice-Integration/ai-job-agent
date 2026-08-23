from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+asyncpg://jobagent:jobagent@localhost:5432/jobagent"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-luna"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
