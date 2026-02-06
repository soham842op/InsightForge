"""
Database Configuration and Session Management

This module sets up SQLAlchemy for async database operations.

Interview Insight:
- We use SQLAlchemy 2.0 style with the new "declarative" syntax
- Session management is critical for proper connection handling
- The dependency injection pattern (get_db) is standard in FastAPI
"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# Create database engine
# 
# Best Practice: Engine configuration explained:
# - pool_pre_ping: Tests connections before using them (handles stale connections)
# - pool_size: Number of connections to keep open
# - max_overflow: Additional connections allowed beyond pool_size
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=settings.debug,  # Log SQL queries in debug mode
)

# Session factory
# 
# autocommit=False: We manually control transactions (explicit is better)
# autoflush=False: Prevents automatic flushing before queries (more predictable)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.
    
    This is a generator that:
    1. Creates a new session for each request
    2. Yields it for use in the endpoint
    3. Automatically closes it when the request is done
    
    Interview Insight:
    This pattern is called "Dependency Injection" - a core concept in
    modern web frameworks. FastAPI's Depends() makes this elegant.
    
    Common Mistake:
    Forgetting to close sessions leads to connection pool exhaustion,
    causing your app to hang under load. The try/finally pattern
    guarantees cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Type alias for cleaner dependency injection in routes
# This is a modern Python pattern using Annotated types
DatabaseSession = Annotated[Session, Depends(get_db)]
