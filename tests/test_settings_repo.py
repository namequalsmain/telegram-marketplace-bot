"""Tests for the settings KV repository."""

import pytest

from database.repo import settings as settings_repo


@pytest.mark.asyncio
async def test_get_missing_returns_default(session):
    assert await settings_repo.get(session, "missing", "fallback") == "fallback"


@pytest.mark.asyncio
async def test_set_then_get(session):
    await settings_repo.set_(session, "foo", "bar")
    assert await settings_repo.get(session, "foo") == "bar"


@pytest.mark.asyncio
async def test_set_overwrites(session):
    await settings_repo.set_(session, "key", "v1")
    await settings_repo.set_(session, "key", "v2")
    assert await settings_repo.get(session, "key") == "v2"


@pytest.mark.asyncio
async def test_get_all(session):
    await settings_repo.set_(session, "a", "1")
    await settings_repo.set_(session, "b", "2")
    assert await settings_repo.get_all(session) == {"a": "1", "b": "2"}
