"""Runtime config: sub-check, required channel, ToS text, support text."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.admin.keyboards import back_to_admin, settings_menu
from bot.callbacks import Admin, AdminSetting
from bot.filters import IsAdmin
from bot.utils import send_or_edit
from database.repo import settings as settings_repo

router = Router(name="admin_settings")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


EDITABLE_KEYS: dict[str, tuple[str, str]] = {
    "required_channel": ("Канал для подписки", "@channel_username или -100…"),
    "tos_text":         ("Текст ToS",          "произвольный текст"),
    "support_text":     ("Текст саппорта",     "произвольный текст"),
}


class SettingForm(StatesGroup):
    waiting_value = State()


async def _show(target, session: AsyncSession) -> None:
    sub_on = await settings_repo.get(session, "sub_check_enabled", "0") == "1"
    channel = await settings_repo.get(session, "required_channel", "")
    text = (
        "<b>⚙️ Настройки</b>\n\n"
        f"Проверка подписки: <b>{'включена' if sub_on else 'выключена'}</b>\n"
        f"Канал: <code>{channel or '—'}</code>"
    )
    await send_or_edit(target, text, settings_menu(sub_on, channel))


@router.callback_query(Admin.filter(F.action == "settings"))
async def cb_open(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    await _show(call, session)


@router.callback_query(AdminSetting.filter(F.action == "toggle_sub"))
async def cb_toggle_sub(call: CallbackQuery, session: AsyncSession) -> None:
    cur = await settings_repo.get(session, "sub_check_enabled", "0") == "1"
    await settings_repo.set_(session, "sub_check_enabled", "0" if cur else "1")
    await _show(call, session)


@router.callback_query(AdminSetting.filter(F.action == "edit"))
async def cb_edit_start(
    call: CallbackQuery, callback_data: AdminSetting, state: FSMContext
) -> None:
    if callback_data.key not in EDITABLE_KEYS:
        await call.answer()
        return
    label, hint = EDITABLE_KEYS[callback_data.key]
    await state.set_state(SettingForm.waiting_value)
    await state.update_data(key=callback_data.key)
    await call.message.answer(
        f"Введи новое значение для «{label}» ({hint}).\n/cancel — отмена."
    )
    await call.answer()


@router.message(SettingForm.waiting_value)
async def form_apply(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    await settings_repo.set_(session, data["key"], (message.text or "").strip())
    await state.clear()
    await message.answer("✅ Сохранено.", reply_markup=back_to_admin())
