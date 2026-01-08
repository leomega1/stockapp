from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
import os

settings = get_settings()

# Get DATABASE_URL from environment (Heroku Postgres addon sets this)
database_url = os.getenv("DATABASE_URL")

if database_url:
    # Fix Heroku Postgres URL format (postgres:// -> postgresql://)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    print(f"Using Postgres database")
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,
        max_overflow=10,
        connect_args={
            "connect_timeout": 10,  # 10 second timeout
            "options": "-c statement_timeout=30000"  # 30 second query timeout
        }
    )
else:
    # Fallback to SQLite for local development
    print(f"Using SQLite database")
    database_url = settings.database_url
    engine = create_engine(database_url, connect_args={"check_same_thread": False})

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

