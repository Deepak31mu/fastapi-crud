"""Unit tests for UserRepository (uses mock DB, no service/HTTP layer)."""

import pytest

from app.models.user import User
from app.repositories.user_repository import UserRepository


@pytest.fixture()
def repo():
    return UserRepository()


class TestUserRepositoryCreate:
    async def test_create(self, mock_db, repo):
        user = User(name="Repo Test", email="repo@example.com")
        created = await repo.create(user)
        assert created.id is not None
        assert created.email == "repo@example.com"


class TestUserRepositoryRead:
    async def test_get_by_id(self, mock_db, repo):
        user = await repo.create(User(name="Find Me", email="find@example.com"))
        found = await repo.get_by_id(str(user.id))
        assert found is not None
        assert found.name == "Find Me"

    async def test_get_by_id_not_found(self, mock_db, repo):
        result = await repo.get_by_id("507f1f77bcf86cd799439011")
        assert result is None

    async def test_get_by_email(self, mock_db, repo):
        await repo.create(User(name="Email Lookup", email="lookup@example.com"))
        found = await repo.get_by_email("lookup@example.com")
        assert found is not None
        assert found.name == "Email Lookup"

    async def test_get_all(self, mock_db, repo):
        for i in range(3):
            await repo.create(User(name=f"User {i}", email=f"all{i}@example.com"))
        users = await repo.get_all(skip=0, limit=10)
        assert len(users) == 3

    async def test_get_all_pagination(self, mock_db, repo):
        for i in range(5):
            await repo.create(User(name=f"Page {i}", email=f"page{i}@example.com"))
        page = await repo.get_all(skip=2, limit=2)
        assert len(page) == 2

    async def test_count(self, mock_db, repo):
        for i in range(4):
            await repo.create(User(name=f"Count {i}", email=f"cnt{i}@example.com"))
        assert await repo.count() == 4


class TestUserRepositoryUpdate:
    async def test_update(self, mock_db, repo):
        user = await repo.create(User(name="Before", email="upd@example.com"))
        updated = await repo.update(str(user.id), {"name": "After"})
        assert updated is not None
        assert updated.name == "After"

    async def test_update_not_found(self, mock_db, repo):
        result = await repo.update("507f1f77bcf86cd799439011", {"name": "Nope"})
        assert result is None


class TestUserRepositoryDelete:
    async def test_delete(self, mock_db, repo):
        user = await repo.create(User(name="Bye", email="bye@example.com"))
        assert await repo.delete(str(user.id)) is True
        assert await repo.get_by_id(str(user.id)) is None

    async def test_delete_not_found(self, mock_db, repo):
        assert await repo.delete("507f1f77bcf86cd799439011") is False
