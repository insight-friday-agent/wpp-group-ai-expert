from __future__ import annotations

import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    whatsapp_api_url: str = "https://api.placehold.it/messages"
    whatsapp_api_token: str = "token-placeholder"
    model_name: str = "claude-sonnet"
    vector_db_url: str = "http://localhost:8000"

    class Config:
        env_prefix = "WPP_"


settings = Settings()
