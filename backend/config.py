from functools import lru_cache
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./recruiting.db"
    secret_key: str = "dev-secret-key-change-in-env-to-a-long-random-value"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    openai_api_key: str | None = None
    rate_limit_per_minute: int = 60
    cors_origins: str = "http://127.0.0.1:8080,http://localhost:8080,http://127.0.0.1:5500,http://localhost:5500"

    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    @property
    def cors_origins_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
