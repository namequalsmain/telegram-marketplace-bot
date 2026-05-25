"""Inline keyboards for the admin side. Russian-only — admin is technical."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.callbacks import (
    Admin,
    AdminCat,
    AdminCatAction,
    AdminProd,
    AdminSetting,
    AdminUserAction,
    Menu,
)
from database.models import Category, Product


def admin_menu() -> InlineKeyboardMarkup:
    items = [
        ("📁 Категории/товары", AdminCat(id=0).pack()),
        ("📣 Рассылка",         Admin(action="broadcast").pack()),
        ("📊 Статистика",       Admin(action="stats").pack()),
        ("👥 Юзеры",            Admin(action="users").pack()),
        ("⚙️ Настройки",        Admin(action="settings").pack()),
        ("« В юзер-меню",       Menu(action="home").pack()),
    ]
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=label, callback_data=cb)] for label, cb in items]
    )


def back_to_admin() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="« В админку", callback_data=Admin(action="home").pack())
        ]]
    )


# ─── Catalog tree (admin view) ──────────────────────────────────────────────
def catalog_node(
    current: Category | None,
    children: list[Category],
    products: list[Product],
) -> InlineKeyboardMarkup:
    """Admin view of a category node — child cats + products + CRUD actions."""
    rows: list[list[InlineKeyboardButton]] = []
    for c in children:
        rows.append([InlineKeyboardButton(text=f"📁 {c.name}", callback_data=AdminCat(id=c.id).pack())])
    for p in products:
        mark = "✅" if p.is_active else "🚫"
        rows.append([InlineKeyboardButton(
            text=f"{mark} 🛍 {p.name} — {p.price} ⭐",
            callback_data=AdminProd(action="view", id=p.id).pack(),
        )])

    cur_id = current.id if current else 0
    rows.append([
        InlineKeyboardButton(text="➕ Подкатегория", callback_data=AdminCatAction(action="add", id=cur_id).pack()),
        InlineKeyboardButton(text="➕ Товар",        callback_data=AdminProd(action="add", id=cur_id).pack()),
    ])
    if current is not None:
        rows.append([
            InlineKeyboardButton(text="✏️ Переименовать", callback_data=AdminCatAction(action="rename", id=current.id).pack()),
            InlineKeyboardButton(text="❌ Удалить",       callback_data=AdminCatAction(action="delete", id=current.id).pack()),
        ])
        back_to = current.parent_id if current.parent_id else 0
        rows.append([InlineKeyboardButton(text="« Назад", callback_data=AdminCat(id=back_to).pack())])
    rows.append([InlineKeyboardButton(text="🏠 В админку", callback_data=Admin(action="home").pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def product_card(product: Product) -> InlineKeyboardMarkup:
    toggle_label = "🚫 Скрыть" if product.is_active else "✅ Показать"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=toggle_label, callback_data=AdminProd(action="toggle", id=product.id).pack()),
                InlineKeyboardButton(text="❌ Удалить",   callback_data=AdminProd(action="delete", id=product.id).pack()),
            ],
            [InlineKeyboardButton(text="« К категории", callback_data=AdminCat(id=product.category_id).pack())],
        ]
    )


# ─── Users sub-menu ─────────────────────────────────────────────────────────
def users_menu() -> InlineKeyboardMarkup:
    items = [
        ("🚫 Бан",              "ban"),
        ("✅ Разбан",           "unban"),
        ("👑 Сделать админом",  "promote"),
        ("👤 Снять админа",     "demote"),
    ]
    rows = [
        [InlineKeyboardButton(text=label, callback_data=AdminUserAction(action=a).pack())]
        for label, a in items
    ]
    rows.append([InlineKeyboardButton(text="« В админку", callback_data=Admin(action="home").pack())])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# ─── Settings sub-menu ──────────────────────────────────────────────────────
def settings_menu(sub_on: bool, channel: str) -> InlineKeyboardMarkup:
    toggle_label = "🔕 Выключить sub-check" if sub_on else "🔔 Включить sub-check"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=toggle_label, callback_data=AdminSetting(action="toggle_sub").pack())],
            [InlineKeyboardButton(
                text=f"📢 Канал: {channel or '— не задан —'}",
                callback_data=AdminSetting(action="edit", key="required_channel").pack(),
            )],
            [InlineKeyboardButton(text="📄 Изменить ToS",   callback_data=AdminSetting(action="edit", key="tos_text").pack())],
            [InlineKeyboardButton(text="🆘 Изменить саппорт", callback_data=AdminSetting(action="edit", key="support_text").pack())],
            [InlineKeyboardButton(text="« В админку",       callback_data=Admin(action="home").pack())],
        ]
    )
