"""User menu: /start, language picker, profile, ToS, support, settings."""

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import Lang, Menu, SettingsAction
from bot.i18n import DEFAULT_LANG, LANGUAGES, t
from bot.user.keyboards import (
    back_to_menu,
    language_picker,
    main_menu,
    settings_menu,
)
from bot.utils import send_or_edit
from database.models import User
from database.repo import settings as settings_repo
from database.repo import users as users_repo

router = Router(name="user")


# ─── Rendering helpers ──────────────────────────────────────────────────────
async def show_menu(target: Message | CallbackQuery, user: User) -> None:
    text = t(user.language, "menu.greeting", name=user.username or "friend")
    await send_or_edit(target, text, main_menu(user.language))


async def show_lang_picker(target: Message | CallbackQuery, picker_target: str) -> None:
    """`picker_target` becomes Lang.target: 'set' on first /start, 'change' from settings."""
    await send_or_edit(target, t(None, "lang.pick"), language_picker(picker_target))


async def show_settings(target: Message | CallbackQuery, user: User) -> None:
    text = t(
        user.language,
        "settings.title",
        lang=LANGUAGES.get(user.language or DEFAULT_LANG, "?"),
    )
    await send_or_edit(target, text, settings_menu(user.language))


# ─── Commands ────────────────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message, user: User) -> None:
    if user.language is None:
        await show_lang_picker(message, picker_target="set")
    else:
        await show_menu(message, user)


# ─── Sub-check passthrough ───────────────────────────────────────────────────
@router.callback_query(F.data == "check_sub")
async def cb_check_sub(call: CallbackQuery, user: User) -> None:
    if user.language is None:
        await show_lang_picker(call, picker_target="set")
    else:
        await show_menu(call, user)


# ─── Language ────────────────────────────────────────────────────────────────
@router.callback_query(Lang.filter())
async def cb_lang(
    call: CallbackQuery, callback_data: Lang, user: User, session: AsyncSession
) -> None:
    if callback_data.code not in LANGUAGES:
        await call.answer()
        return
    await users_repo.set_language(session, user, callback_data.code)
    await call.answer(t(callback_data.code, "lang.changed"))
    # After picking, go to main menu (first time) or back to settings (change)
    if callback_data.target == "set":
        await show_menu(call, user)
    else:
        await show_settings(call, user)


# ─── Main menu actions ───────────────────────────────────────────────────────
@router.callback_query(Menu.filter(F.action == "home"))
async def cb_home(call: CallbackQuery, user: User) -> None:
    await show_menu(call, user)


@router.callback_query(Menu.filter(F.action == "profile"))
async def cb_profile(call: CallbackQuery, user: User) -> None:
    text = t(
        user.language,
        "profile.text",
        id=user.user_id,
        username=user.username or "—",
        balance=user.balance,
        reg_date=user.reg_date.strftime("%Y-%m-%d %H:%M"),
    )
    await send_or_edit(call, text, back_to_menu(user.language))


@router.callback_query(Menu.filter(F.action == "tos"))
async def cb_tos(call: CallbackQuery, user: User, session: AsyncSession) -> None:
    body = await settings_repo.get(session, "tos_text", t(user.language, "tos.empty"))
    text = f"{t(user.language, 'tos.title')}\n\n{body}"
    await send_or_edit(call, text, back_to_menu(user.language))


@router.callback_query(Menu.filter(F.action == "support"))
async def cb_support(call: CallbackQuery, user: User, session: AsyncSession) -> None:
    body = await settings_repo.get(session, "support_text", t(user.language, "support.empty"))
    text = f"{t(user.language, 'support.title')}\n\n{body}"
    await send_or_edit(call, text, back_to_menu(user.language))


@router.callback_query(Menu.filter(F.action == "settings"))
async def cb_settings(call: CallbackQuery, user: User) -> None:
    await show_settings(call, user)


@router.callback_query(SettingsAction.filter(F.action == "open_lang"))
async def cb_settings_lang(call: CallbackQuery) -> None:
    await show_lang_picker(call, picker_target="change")
