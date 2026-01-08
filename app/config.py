from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # Heroku sets DATABASE_URL automatically when you add Postgres
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./stockapp.db")
    anthropic_api_key: str = ""
    alpha_vantage_api_key: str = ""
    news_api_key: str = ""
    scheduler_enabled: bool = True
    environment: str = "development"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()

