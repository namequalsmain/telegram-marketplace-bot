"""Copy-message broadcast to all non-banned users.

Telegram allows ~30 messages/sec to different users — we throttle to ~25.
On TelegramForbiddenError (user blocked the bot) we mark them banned to skip next time.
"""

import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.admin.keyboards import back_to_admin
from bot.callbacks import Admin, AdminBroadcast
from bot.filters import IsAdmin
from bot.utils import send_or_edit
from database.repo import users as users_repo
from database.session import async_session_maker

router = Router(name="admin_broadcast")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

log = logging.getLogger("broadcast")


class BroadcastForm(StatesGroup):
    waiting_message = State()
    confirm = State()


def _confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="✅ Отправить", callback_data=AdminBroadcast(action="send").pack()),
            InlineKeyboardButton(text="❌ Отмена",   callback_data=AdminBroadcast(action="cancel").pack()),
        ]]
    )


@router.callback_query(Admin.filter(F.action == "broadcast"))
async def cb_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BroadcastForm.waiting_message)
    text = (
        "📣 <b>Рассылка</b>\n\n"
        "Пришли сообщение (текст / фото / видео — что угодно), оно будет разослано всем юзерам.\n"
        "/cancel — отмена."
    )
    await send_or_edit(call, text, back_to_admin())


@router.message(BroadcastForm.waiting_message)
async def got_message(message: Message, state: FSMContext) -> None:
    await state.update_data(from_chat_id=message.chat.id, message_id=message.message_id)
    await state.set_state(BroadcastForm.confirm)
    await message.answer("Превью выше. Подтвердить рассылку?", reply_markup=_confirm_keyboard())


@router.callback_query(AdminBroadcast.filter(F.action == "cancel"), BroadcastForm.confirm)
async def cb_cancel(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await send_or_edit(call, "Отменено.", back_to_admin())


@router.callback_query(AdminBroadcast.filter(F.action == "send"), BroadcastForm.confirm)
async def cb_send(
    call: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    data = await state.get_data()
    await state.clear()

    recipients = await users_repo.all_active_ids(session)
    await send_or_edit(call, f"⏳ Рассылка запущена для {len(recipients)} юзеров…")

    asyncio.create_task(
        _send_to_all(bot, recipients, data["from_chat_id"], data["message_id"], call.from_user.id)
    )


async def _send_to_all(
    bot: Bot, user_ids: list[int], from_chat_id: int, message_id: int, notify_admin: int
) -> None:
    sent = failed = blocked = 0

    for uid in user_ids:
        try:
            await bot.copy_message(uid, from_chat_id, message_id)
            sent += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await bot.copy_message(uid, from_chat_id, message_id)
                sent += 1
            except Exception:
                failed += 1
        except TelegramForbiddenError:
            blocked += 1
            await _mark_blocked(uid)
        except TelegramBadRequest:
            failed += 1
        except Exception as e:
            log.exception("broadcast error for %s: %s", uid, e)
            failed += 1
        await asyncio.sleep(0.04)  # ~25 msg/sec

    summary = (
        "📣 Рассылка завершена.\n\n"
        f"✅ Доставлено: <b>{sent}</b>\n"
        f"🚫 Заблокировали бота: <b>{blocked}</b>\n"
        f"⚠️ Ошибок: <b>{failed}</b>"
    )
    try:
        await bot.send_message(notify_admin, summary)
    except Exception:
        pass


async def _mark_blocked(user_id: int) -> None:
    """User blocked the bot — silently skip them next time."""
    try:
        async with async_session_maker() as s:
            user = await users_repo.get(s, user_id)
            if user:
                await users_repo.set_ban(s, user, True)
    except Exception:
        pass
