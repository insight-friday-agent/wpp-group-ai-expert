from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    whatsapp_api_url: str = "https://api.placehold.it/messages"
    whatsapp_api_token: str = "token-placeholder"
    model_name: str = "claude-sonnet"
    vector_db_url: str = "http://localhost:8000"
    pg_host: str = "localhost"
    pg_port: int = 5432
    pg_user: str = "postgres"
    pg_password: str = "postgres"
    pg_db: str = "wpp"
    vector_dim: int = 8

    class Config:
        env_prefix = "WPP_"


settings = Settings()
