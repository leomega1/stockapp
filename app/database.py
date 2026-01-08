from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
import os

settings = get_settings()

# Use SQLite for now (simpler, no Postgres addon needed)
# Data will reset on dyno restart, but we can trigger fresh fetches easily
print(f"Using SQLite database")
database_url = "sqlite:///./stockapp.db"
engine = create_engine(
    database_url,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)

