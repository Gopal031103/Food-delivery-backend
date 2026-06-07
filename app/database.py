"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base model
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session in routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    # """Create all database tables."""
    # Base.metadata.create_all(bind=engine)
    # logger.info("Database tables created successfully")
    print("Tables found:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def init_db():
    """Initialize database connection and create tables."""
    try:
        create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise
