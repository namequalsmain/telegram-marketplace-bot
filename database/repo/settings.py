"""Runtime key-value settings (editable by admin without restart)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Setting


async def get(session: AsyncSession, key: str, default: str = "") -> str:
    s = await session.get(Setting, key)
    return s.value if s else default


async def set_(session: AsyncSession, key: str, value: str) -> None:
    s = await session.get(Setting, key)
    if s is None:
        session.add(Setting(key=key, value=value))
    else:
        s.value = value
    await session.commit()


async def get_all(session: AsyncSession) -> dict[str, str]:
    rows = await session.execute(select(Setting))
    return {s.key: s.value for s in rows.scalars().all()}
