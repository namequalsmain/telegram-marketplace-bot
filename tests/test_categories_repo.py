"""Tests for the categories repository — focus on tree navigation."""

import pytest

from database.repo import categories as categories_repo


@pytest.mark.asyncio
async def test_create_and_list_top_level(session):
    a = await categories_repo.create(session, parent_id=None, name="Drinks")
    b = await categories_repo.create(session, parent_id=None, name="Snacks")

    top = await categories_repo.children_of(session, None)
    names = [c.name for c in top]
    assert {"Drinks", "Snacks"} <= set(names)
    assert all(c.parent_id is None for c in top)
    _ = a, b  # silence unused


@pytest.mark.asyncio
async def test_nested_children(session):
    root = await categories_repo.create(session, parent_id=None, name="Drinks")
    sub = await categories_repo.create(session, parent_id=root.id, name="Coffee")

    children = await categories_repo.children_of(session, root.id)
    assert len(children) == 1
    assert children[0].id == sub.id


@pytest.mark.asyncio
async def test_breadcrumbs_returns_root_to_leaf(session):
    a = await categories_repo.create(session, parent_id=None, name="A")
    b = await categories_repo.create(session, parent_id=a.id, name="B")
    c = await categories_repo.create(session, parent_id=b.id, name="C")

    chain = await categories_repo.breadcrumbs(session, c.id)
    assert [cat.name for cat in chain] == ["A", "B", "C"]


@pytest.mark.asyncio
async def test_delete_cascades_to_children(session):
    root = await categories_repo.create(session, parent_id=None, name="Root")
    child = await categories_repo.create(session, parent_id=root.id, name="Child")

    await categories_repo.delete(session, root)
    assert await categories_repo.get(session, child.id) is None
