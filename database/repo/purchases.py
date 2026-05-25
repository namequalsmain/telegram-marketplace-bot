"""Purchase operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Purchase


async def record(
    session: AsyncSession,
    *,
    user_id: int,
    product_id: int | None,
    price: int,
    charge_id: str | None,
) -> Purchase:
    p = Purchase(
        user_id=user_id,
        product_id=product_id,
        price=price,
        status="paid",
        telegram_payment_charge_id=charge_id,
    )
    session.add(p)
    await session.commit()
    return p


async def count_total(session: AsyncSession) -> int:
    return (await session.execute(select(func.count(Purchase.id)))).scalar() or 0


async def revenue_total(session: AsyncSession) -> int:
    return (
        await session.execute(select(func.coalesce(func.sum(Purchase.price), 0)))
    ).scalar() or 0
