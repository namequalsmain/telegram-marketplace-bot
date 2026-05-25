"""Inline keyboards for the user side. Pure UI — no DB calls."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.callbacks import Catalog, Lang, Menu, SettingsAction
from bot.i18n import LANGUAGES, t
from database.models import Category, Product


def language_picker(target: str) -> InlineKeyboardMarkup:
    """target='set' for first-time pick, 'change' for in-settings change."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=Lang(target=target, code=code).pack())]
            for code, label in LANGUAGES.items()
        ]
    )


def main_menu(lang: str | None) -> InlineKeyboardMarkup:
    items = [
        ("menu.btn.profile",  "profile"),
        ("menu.btn.catalog",  None),  # special: goes to catalog root
        ("menu.btn.support",  "support"),
        ("menu.btn.tos",      "tos"),
        ("menu.btn.settings", "settings"),
    ]
    rows: list[list[InlineKeyboardButton]] = []
    for key, action in items:
        if action is None:
            cb = Catalog(id=0).pack()
        else:
            cb = Menu(action=action).pack()
        rows.append([InlineKeyboardButton(text=t(lang, key), callback_data=cb)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_to_menu(lang: str | None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text=t(lang, "menu.btn.back"), callback_data=Menu(action="home").pack())
        ]]
    )


def settings_menu(lang: str | None) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=t(lang, "settings.btn.lang"),
                callback_data=SettingsAction(action="open_lang").pack(),
            )],
            [InlineKeyboardButton(
                text=t(lang, "menu.btn.back"),
                callback_data=Menu(action="home").pack(),
            )],
        ]
    )


# ─── Catalog ─────────────────────────────────────────────────────────────────
def catalog_node(
    children: list[Category],
    products: list[Product],
    back_to: int | None,
    lang: str | None,
) -> InlineKeyboardMarkup:
    """Keyboard for a category page. `back_to`=None means current node is root."""
    from bot.callbacks import Product as ProdCb

    rows: list[list[InlineKeyboardButton]] = []
    for c in children:
        rows.append([InlineKeyboardButton(text=f"📁 {c.name}", callback_data=Catalog(id=c.id).pack())])
    for p in products:
        rows.append([InlineKeyboardButton(
            text=f"🛍 {p.name} — {p.price} ⭐",
            callback_data=ProdCb(action="view", id=p.id).pack(),
        )])
    if back_to is not None:
        rows.append([InlineKeyboardButton(
            text=t(lang, "catalog.btn.back"),
            callback_data=Catalog(id=back_to).pack(),
        )])
    rows.append([InlineKeyboardButton(
        text=t(lang, "catalog.btn.home"),
        callback_data=Menu(action="home").pack(),
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def product_card(product: Product, lang: str | None) -> InlineKeyboardMarkup:
    from bot.callbacks import Product as ProdCb

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=t(lang, "product.btn.buy", price=product.price),
                callback_data=ProdCb(action="buy", id=product.id).pack(),
            )],
            [InlineKeyboardButton(
                text=t(lang, "catalog.btn.back"),
                callback_data=Catalog(id=product.category_id).pack(),
            )],
        ]
    )
