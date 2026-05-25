"""Tests for the users repository."""

import pytest

from database.repo import users as users_repo


@pytest.mark.asyncio
async def test_get_or_create_creates_new_user(session):
    user = await users_repo.get_or_create(session, user_id=42, username="alice")
    assert user.user_id == 42
    assert user.username == "alice"
    assert user.balance == 0
    assert user.is_admin is False
    assert user.is_banned is False


@pytest.mark.asyncio
async def test_get_or_create_updates_username(session):
    await users_repo.get_or_create(session, user_id=42, username="alice")
    user = await users_repo.get_or_create(session, user_id=42, username="alice_new")
    assert user.username == "alice_new"


@pytest.mark.asyncio
async def test_set_language_persists(session):
    user = await users_repo.get_or_create(session, user_id=1, username="x")
    await users_repo.set_language(session, user, "en")
    refetched = await users_repo.get(session, 1)
    assert refetched.language == "en"


@pytest.mark.asyncio
async def test_set_ban_excludes_from_active_ids(session):
    a = await users_repo.get_or_create(session, user_id=1, username="a")
    b = await users_repo.get_or_create(session, user_id=2, username="b")
    await users_repo.set_ban(session, b, True)

    active = await users_repo.all_active_ids(session)
    assert a.user_id in active
    assert b.user_id not in active


@pytest.mark.asyncio
async def test_counts(session):
    await users_repo.get_or_create(session, user_id=1, username="a")
    u2 = await users_repo.get_or_create(session, user_id=2, username="b")
    u3 = await users_repo.get_or_create(session, user_id=3, username="c")
    await users_repo.set_ban(session, u2, True)
    await users_repo.set_admin(session, u3, True)

    assert await users_repo.count_total(session) == 3
    assert await users_repo.count_banned(session) == 1
    assert await users_repo.count_admins(session) == 1
