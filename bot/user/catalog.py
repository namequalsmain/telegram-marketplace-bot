"""Browse catalog: categories → subcategories → product card."""

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import Catalog
from bot.callbacks import Product as ProductCb
from bot.i18n import t
from bot.user.keyboards import catalog_node, product_card
from bot.utils import send_or_edit
from database.models import User
from database.repo import categories as categories_repo
from database.repo import products as products_repo

router = Router(name="user_catalog")


def _format_breadcrumbs(crumbs: list, lang: str | None) -> str:
    """Render breadcrumb chain with the localized root label."""
    parts = [t(lang, "catalog.root")] + [c.name for c in crumbs]
    return " › ".join(parts)


@router.callback_query(Catalog.filter())
async def cb_open(
    call: CallbackQuery, callback_data: Catalog, user: User, session: AsyncSession
) -> None:
    # id=0 → virtual root; load top-level categories with no parent.
    if callback_data.id == 0:
        crumbs: list = []
        children = await categories_repo.children_of(session, None)
        products = []
        back_to = None  # no back button at root
    else:
        category = await categories_repo.get(session, callback_data.id)
        if category is None:
            await call.answer(t(user.language, "catalog.notfound"), show_alert=True)
            return
        crumbs = await categories_repo.breadcrumbs(session, category.id)
        children = await categories_repo.children_of(session, category.id)
        products = await products_repo.in_category(session, category.id, only_active=True)
        back_to = category.parent_id if category.parent_id else 0

    body_key = "catalog.empty" if not children and not products else "catalog.pick"
    text = f"<b>{_format_breadcrumbs(crumbs, user.language)}</b>\n\n{t(user.language, body_key)}"
    await send_or_edit(call, text, catalog_node(children, products, back_to, user.language))


@router.callback_query(ProductCb.filter(F.action == "view"))
async def cb_view(
    call: CallbackQuery, callback_data: ProductCb, user: User, session: AsyncSession
) -> None:
    product = await products_repo.get(session, callback_data.id)
    if product is None or not product.is_active:
        await call.answer(t(user.language, "product.unavail"), show_alert=True)
        return

    desc = product.description or t(user.language, "product.no_desc")
    text = (
        f"<b>🛍 {product.name}</b>\n\n"
        f"{desc}\n\n"
        f"{t(user.language, 'product.price', price=product.price)}"
    )
    kb = product_card(product, user.language)

    # With a photo we send a new photo-message; otherwise edit in place.
    if product.photo_file_id:
        try:
            await call.message.delete()
        except TelegramBadRequest:
            pass
        await call.message.answer_photo(product.photo_file_id, caption=text, reply_markup=kb)
        await call.answer()
    else:
        await send_or_edit(call, text, kb)
