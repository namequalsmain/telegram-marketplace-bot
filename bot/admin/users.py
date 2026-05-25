"""User management: ban / unban / promote / demote by user_id."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.admin.keyboards import back_to_admin, users_menu
from bot.callbacks import Admin, AdminUserAction
from bot.filters import IsAdmin
from bot.utils import send_or_edit
from config import settings as cfg
from database.repo import users as users_repo

router = Router(name="admin_users")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


class UserForm(StatesGroup):
    waiting_id = State()


ACTION_PROMPT = {
    "ban":     "Введи user_id для бана:",
    "unban":   "Введи user_id для разбана:",
    "promote": "Введи user_id, кого назначить админом:",
    "demote":  "Введи user_id, у кого забрать права админа:",
}


@router.callback_query(Admin.filter(F.action == "users"))
async def cb_users(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await send_or_edit(call, "<b>👥 Управление юзерами</b>\n\nВыбери действие:", users_menu())


@router.callback_query(AdminUserAction.filter())
async def cb_pick_action(
    call: CallbackQuery, callback_data: AdminUserAction, state: FSMContext
) -> None:
    if callback_data.action not in ACTION_PROMPT:
        await call.answer()
        return
    await state.set_state(UserForm.waiting_id)
    await state.update_data(action=callback_data.action)
    await call.message.answer(ACTION_PROMPT[callback_data.action] + "\n/cancel — отмена.")
    await call.answer()


@router.message(UserForm.waiting_id)
async def form_apply(message: Message, state: FSMContext, session: AsyncSession) -> None:
    raw = (message.text or "").strip()
    try:
        uid = int(raw)
    except ValueError:
        await message.answer("user_id — это число. Попробуй ещё раз:")
        return

    data = await state.get_data()
    action = data["action"]
    await state.clear()

    user = await users_repo.get(session, uid)
    if user is None:
        await message.answer("Юзера с таким ID нет в базе.", reply_markup=back_to_admin())
        return
    if uid == cfg.MAIN_ADMIN_ID and action in {"ban", "demote"}:
        await message.answer("Главного админа трогать нельзя.", reply_markup=back_to_admin())
        return

    if action == "ban":
        await users_repo.set_ban(session, user, True)
        msg = f"🚫 Юзер {uid} забанен."
    elif action == "unban":
        await users_repo.set_ban(session, user, False)
        msg = f"✅ Юзер {uid} разбанен."
    elif action == "promote":
        await users_repo.set_admin(session, user, True)
        msg = f"👑 Юзер {uid} теперь админ."
    else:  # demote
        await users_repo.set_admin(session, user, False)
        msg = f"👤 У юзера {uid} забраны права админа."
    await message.answer(msg, reply_markup=back_to_admin())
