"""Engine + session factory.

DB schema is managed by Alembic (see `alembic/`). On startup, the Docker
entrypoint runs `alembic upgrade head` before the bot starts. After that,
`seed_defaults_and_bootstrap_admin()` populates default settings and ensures
the main admin from .env has admin rights.
"""

import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings as cfg
from database.models import User
from database.repo import settings as settings_repo

log = logging.getLogger("database.session")

engine = create_async_engine(cfg.DSN, echo=False, pool_pre_ping=True)
async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


DEFAULT_SETTINGS: dict[str, str] = {
    "sub_check_enabled": "0",
    "required_channel": "",
    "tos_text": "Здесь будет текст пользовательского соглашения.",
    "support_text": "По всем вопросам пишите: @your_support",
}


async def _seed_defaults(session: AsyncSession) -> None:
    for key, value in DEFAULT_SETTINGS.items():
        current = await settings_repo.get(session, key, default="__missing__")
        if current == "__missing__":
            await settings_repo.set_(session, key, value)


async def _bootstrap_admin(session: AsyncSession) -> None:
    if not cfg.MAIN_ADMIN_ID:
        return
    user = await session.get(User, cfg.MAIN_ADMIN_ID)
    if user is None:
        user = User(user_id=cfg.MAIN_ADMIN_ID, is_admin=True)
        session.add(user)
    elif not user.is_admin:
        user.is_admin = True
    await session.commit()


async def seed_defaults_and_bootstrap_admin() -> None:
    """Idempotent — safe to run on every startup."""
    async with async_session_maker() as session:
        await _seed_defaults(session)
        await _bootstrap_admin(session)
    log.info("Default settings seeded; main admin ensured")
