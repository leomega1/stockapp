from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "sqlite:///./stockapp.db"
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

