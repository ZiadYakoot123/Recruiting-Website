from functools import lru_cache
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./recruiting.db"
    secret_key: str = "change_me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    openai_api_key: str | None = None
    rate_limit_per_minute: int = 60

    model_config = ConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
