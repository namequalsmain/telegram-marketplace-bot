"""User operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


async def get(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def get_or_create(session: AsyncSession, user_id: int, username: str | None) -> User:
    user = await session.get(User, user_id)
    if user is None:
        user = User(user_id=user_id, username=username)
        session.add(user)
        await session.commit()
    elif user.username != username:
        user.username = username
        await session.commit()
    return user


async def set_language(session: AsyncSession, user: User, lang: str) -> None:
    user.language = lang
    await session.commit()


async def set_ban(session: AsyncSession, user: User, banned: bool) -> None:
    user.is_banned = banned
    await session.commit()


async def set_admin(session: AsyncSession, user: User, admin: bool) -> None:
    user.is_admin = admin
    await session.commit()


async def all_active_ids(session: AsyncSession) -> list[int]:
    """Non-banned users — recipients for broadcast."""
    rows = await session.execute(
        select(User.user_id).where(User.is_banned.is_(False))
    )
    return [row[0] for row in rows.all()]


async def count_total(session: AsyncSession) -> int:
    return (await session.execute(select(func.count(User.user_id)))).scalar() or 0


async def count_banned(session: AsyncSession) -> int:
    return (
        await session.execute(
            select(func.count(User.user_id)).where(User.is_banned.is_(True))
        )
    ).scalar() or 0


async def count_admins(session: AsyncSession) -> int:
    return (
        await session.execute(
            select(func.count(User.user_id)).where(User.is_admin.is_(True))
        )
    ).scalar() or 0
