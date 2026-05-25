from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class IsAdmin(Filter):
    """Passes only for users with `is_admin=True`."""

    async def __call__(
        self, event: Message | CallbackQuery, session: AsyncSession
    ) -> bool:
        if event.from_user is None:
            return False
        user = await session.get(User, event.from_user.id)
        return bool(user and user.is_admin)
