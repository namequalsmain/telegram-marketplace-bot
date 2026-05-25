"""Force-subscribe gate. Enabled via the `sub_check_enabled` setting."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    TelegramObject,
)

from bot.i18n import t
from database.models import User
from database.repo import settings as settings_repo

SUBSCRIBED_STATUSES = {"member", "administrator", "creator"}


async def _is_subscribed(bot: Bot, channel: str, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(channel, user_id)
    except TelegramBadRequest:
        # Bot not in channel / channel invalid — don't block users.
        return True
    return member.status in SUBSCRIBED_STATUSES


def _gate_keyboard(channel: str, lang: str | None) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if channel.startswith("@"):
        url = f"https://t.me/{channel.lstrip('@')}"
        rows.append([InlineKeyboardButton(text=t(lang, "sub.btn.channel"), url=url)])
    rows.append([InlineKeyboardButton(text=t(lang, "sub.btn.check"), callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("user")
        session = data.get("session")
        bot: Bot = data["bot"]

        if user is None or session is None or user.is_admin:
            return await handler(event, data)
        if isinstance(event, CallbackQuery) and event.data == "check_sub":
            return await handler(event, data)

        cfg = await settings_repo.get_all(session)
        if cfg.get("sub_check_enabled") != "1":
            return await handler(event, data)
        channel = cfg.get("required_channel", "").strip()
        if not channel:
            return await handler(event, data)
        if await _is_subscribed(bot, channel, user.user_id):
            return await handler(event, data)

        # Show the gate
        text = t(user.language, "sub.required")
        kb = _gate_keyboard(channel, user.language)
        if isinstance(event, Message):
            await event.answer(text, reply_markup=kb)
        elif isinstance(event, CallbackQuery):
            await event.answer(t(user.language, "sub.not_yet"), show_alert=True)
            if event.message:
                try:
                    await event.message.edit_text(text, reply_markup=kb)
                except TelegramBadRequest:
                    await event.message.answer(text, reply_markup=kb)
        return
