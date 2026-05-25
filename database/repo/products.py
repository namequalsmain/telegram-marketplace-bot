"""Product operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product


async def get(session: AsyncSession, product_id: int) -> Product | None:
    return await session.get(Product, product_id)


async def in_category(
    session: AsyncSession, category_id: int, *, only_active: bool = False
) -> list[Product]:
    stmt = select(Product).where(Product.category_id == category_id)
    if only_active:
        stmt = stmt.where(Product.is_active.is_(True))
    stmt = stmt.order_by(Product.name)
    rows = await session.execute(stmt)
    return list(rows.scalars().all())


async def create(
    session: AsyncSession,
    *,
    category_id: int,
    name: str,
    description: str,
    price: int,
    photo_file_id: str | None,
) -> Product:
    p = Product(
        category_id=category_id,
        name=name,
        description=description,
        price=price,
        photo_file_id=photo_file_id,
    )
    session.add(p)
    await session.commit()
    return p


async def toggle_active(session: AsyncSession, product: Product) -> None:
    product.is_active = not product.is_active
    await session.commit()


async def delete(session: AsyncSession, product: Product) -> None:
    await session.delete(product)
    await session.commit()


async def count_total(session: AsyncSession) -> int:
    return (await session.execute(select(func.count(Product.id)))).scalar() or 0
