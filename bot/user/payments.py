"""Telegram Stars (XTR) payments.

Flow:
  1. cb_buy → bot.send_invoice (currency=XTR, no provider_token)
  2. on_pre_checkout → confirm
  3. on_successful_payment → record purchase, ack user
"""

from aiogram import F, Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import Menu
from bot.callbacks import Product as ProductCb
from bot.i18n import t
from database.models import User
from database.repo import products as products_repo
from database.repo import purchases as purchases_repo

router = Router(name="user_payments")


@router.callback_query(ProductCb.filter(F.action == "buy"))
async def cb_buy(
    call: CallbackQuery, callback_data: ProductCb, user: User, session: AsyncSession
) -> None:
    product = await products_repo.get(session, callback_data.id)
    if product is None or not product.is_active:
        await call.answer(t(user.language, "product.unavail"), show_alert=True)
        return

    await call.message.answer_invoice(
        title=product.name[:32] or "Item",
        description=(product.description or product.name)[:255],
        payload=f"product:{product.id}",
        provider_token="",            # empty → Telegram Stars
        currency="XTR",
        prices=[LabeledPrice(label=product.name[:32], amount=product.price)],
    )
    await call.answer()


@router.pre_checkout_query()
async def on_pre_checkout(query: PreCheckoutQuery) -> None:
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: Message, user: User, session: AsyncSession) -> None:
    sp = message.successful_payment

    product_id: int | None = None
    if sp.invoice_payload.startswith("product:"):
        try:
            product_id = int(sp.invoice_payload.split(":", 1)[1])
        except ValueError:
            product_id = None
    product = await products_repo.get(session, product_id) if product_id else None

    await purchases_repo.record(
        session,
        user_id=user.user_id,
        product_id=product.id if product else None,
        price=sp.total_amount,
        charge_id=sp.telegram_payment_charge_id,
    )

    text = t(user.language, "pay.ok", name=product.name if product else "—", amount=sp.total_amount)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text=t(user.language, "catalog.btn.home"),
                callback_data=Menu(action="home").pack(),
            )
        ]]
    )
    await message.answer(text, reply_markup=kb)
