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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Heroku Postgres URLs start with postgres://, but SQLAlchemy needs postgresql://
        if self.database_url and self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)


@lru_cache()
def get_settings():
    return Settings()

