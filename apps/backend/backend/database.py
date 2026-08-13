"""
Database connection and session management.
"""
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import settings

# Configure database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

# Configure session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency for getting database sessions.
    Use this in FastAPI endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    For development only. Use Alembic migrations in production.
    """
    # Import all models to ensure they are registered
    from backend.models import user, career_profile, cv, job_opportunity  # noqa
    from backend.models import job_application, interview, follow_up  # noqa
    from backend.models import document, cv_job_match, chat_message  # noqa
    from backend.models import ai_agent_actions  # noqa

    Base.metadata.create_all(bind=engine)


# Event listeners for connection pooling
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Set PRAGMA for MySQL connection.
    This ensures proper charset handling.
    """
    pass
