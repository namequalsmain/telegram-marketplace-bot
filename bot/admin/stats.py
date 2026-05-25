"""Aggregated stats screen."""

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.admin.keyboards import back_to_admin
from bot.callbacks import Admin
from bot.filters import IsAdmin
from bot.utils import send_or_edit
from database.repo import products as products_repo
from database.repo import purchases as purchases_repo
from database.repo import users as users_repo

router = Router(name="admin_stats")
router.callback_query.filter(IsAdmin())


@router.callback_query(Admin.filter(F.action == "stats"))
async def cb_stats(call: CallbackQuery, session: AsyncSession) -> None:
    users_total   = await users_repo.count_total(session)
    users_banned  = await users_repo.count_banned(session)
    admins_total  = await users_repo.count_admins(session)
    products      = await products_repo.count_total(session)
    purchases     = await purchases_repo.count_total(session)
    revenue       = await purchases_repo.revenue_total(session)

    text = (
        "<b>📊 Статистика</b>\n\n"
        f"👥 Пользователей: <b>{users_total}</b>\n"
        f"   • забанено: {users_banned}\n"
        f"   • админов: {admins_total}\n\n"
        f"🛍 Товаров: <b>{products}</b>\n"
        f"🧾 Покупок: <b>{purchases}</b>\n"
        f"⭐ Выручка: <b>{revenue}</b>"
    )
    await send_or_edit(call, text, back_to_admin())
