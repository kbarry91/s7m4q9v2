"""Database engine, session factory, and ORM base."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./weather.db"

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base that all ORM models inherit from."""


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session per request, closing it afterwards."""
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    # Import all models here to ensure they are registered with the metadata before creating tables.
    from app.persistence import models

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
