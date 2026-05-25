"""Category tree operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Category


async def get(session: AsyncSession, category_id: int) -> Category | None:
    return await session.get(Category, category_id)


async def children_of(session: AsyncSession, parent_id: int | None) -> list[Category]:
    """Direct children of a category. parent_id=None → top-level categories."""
    clause = (
        Category.parent_id.is_(None)
        if parent_id is None
        else Category.parent_id == parent_id
    )
    rows = await session.execute(
        select(Category).where(clause).order_by(Category.sort_order, Category.name)
    )
    return list(rows.scalars().all())


async def breadcrumbs(session: AsyncSession, leaf_id: int) -> list[Category]:
    """Path from root → leaf, inclusive. Empty list if leaf not found.

    Depth is bounded by admin (typical pet-shop tree is 2-4 levels),
    so an O(depth) walk is fine.
    """
    chain: list[Category] = []
    cur_id: int | None = leaf_id
    while cur_id is not None:
        cat = await session.get(Category, cur_id)
        if cat is None:
            break
        chain.append(cat)
        cur_id = cat.parent_id
    return list(reversed(chain))


async def create(session: AsyncSession, parent_id: int | None, name: str) -> Category:
    cat = Category(parent_id=parent_id, name=name)
    session.add(cat)
    await session.commit()
    return cat


async def rename(session: AsyncSession, category: Category, new_name: str) -> None:
    category.name = new_name
    await session.commit()


async def delete(session: AsyncSession, category: Category) -> None:
    await session.delete(category)  # cascades to children + products
    await session.commit()
