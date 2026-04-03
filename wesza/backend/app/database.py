"""
Database configuration and session management.

This module initializes SQLAlchemy engine and provides session factories
for database operations with Supabase PostgreSQL.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# Create async engine for PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENV == "development",  # Log SQL queries in development
    pool_pre_ping=True,  # Verify connections before use
    pool_size=10,  # Number of connections to keep open
    max_overflow=20,  # Max connections beyond pool_size
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        AsyncSession: Database session instance.
        
    Example:
        ```python
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            # Use db session here
        ```
    """
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


async def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    This should be called during application startup.
    Uses Base.metadata.create_all() to create tables defined in models.
    """
    from app.models import user, app, template  # noqa: F401
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections.
    
    This should be called during application shutdown.
    """
    await engine.dispose()
