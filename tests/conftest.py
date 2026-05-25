"""Shared pytest fixtures.

We spin up an **in-memory SQLite** database for each test. SQLAlchemy speaks both
PG and SQLite, and our models don't use Postgres-specific features, so this keeps
tests fast and dependency-free (no PG required in CI).
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from database.models import Base


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    """Fresh schema per test → no cross-test pollution."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as s:
        yield s

    await engine.dispose()
