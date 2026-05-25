"""Admin entry point: /admin command, top-level menu, global /cancel."""

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.admin.keyboards import admin_menu, back_to_admin
from bot.callbacks import Admin
from bot.filters import IsAdmin
from bot.utils import send_or_edit

router = Router(name="admin")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


ADMIN_HEADER = "<b>🛠 Админ-панель</b>\n\nВыбери раздел:"


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    await message.answer(ADMIN_HEADER, reply_markup=admin_menu())


@router.callback_query(Admin.filter(F.action == "home"))
async def cb_home(call: CallbackQuery) -> None:
    await send_or_edit(call, ADMIN_HEADER, admin_menu())


# Global /cancel — works inside ANY admin FSM
@router.message(StateFilter("*"), Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        return
    await state.clear()
    await message.answer("Отменено.", reply_markup=back_to_admin())
