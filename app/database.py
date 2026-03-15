import os
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Used for local development with .env.
    """

    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int | None = None
    DB_NAME: str | None = None

    SECRET_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()

# --- Database URL ---
# On Render the DATABASE_URL env variable is provided automatically
DATABASE_URL = os.getenv("DATABASE_URL")

# If not running on Render, build URL from .env values
if not DATABASE_URL:
    DATABASE_URL = (
        f"postgresql+psycopg://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )

# Render sometimes provides postgres:// instead of postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# --- Create engine ---
try:
    engine = create_engine(DATABASE_URL)
except SQLAlchemyError as exc:
    raise RuntimeError(
        "Failed to connect to the PostgreSQL database."
    ) from exc


# --- Session ---
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# --- Base model ---
class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    """
    pass


# --- Dependency for FastAPI ---
def get_db():
    """
    FastAPI dependency that provides a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()