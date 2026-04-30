"""Unit tests for UserService (uses mock DB, no HTTP layer)."""

import pytest

from app.exceptions.handlers import DuplicateEntityError, EntityNotFoundError
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService


@pytest.fixture()
def service():
    return UserService(repository=UserRepository())


class TestUserServiceCreate:
    async def test_create_user(self, mock_db, service):
        payload = UserCreate(name="Service Test", email="svc@example.com")
        user = await service.create_user(payload)
        assert user.name == "Service Test"
        assert user.email == "svc@example.com"
        assert user.id is not None

    async def test_create_duplicate_raises(self, mock_db, service):
        payload = UserCreate(name="Dup", email="dup@example.com")
        await service.create_user(payload)
        with pytest.raises(DuplicateEntityError):
            await service.create_user(payload)


class TestUserServiceRead:
    async def test_get_existing_user(self, mock_db, service):
        payload = UserCreate(name="Reader", email="read@example.com")
        created = await service.create_user(payload)
        fetched = await service.get_user(str(created.id))
        assert fetched.email == "read@example.com"

    async def test_get_missing_user_raises(self, mock_db, service):
        with pytest.raises(EntityNotFoundError):
            await service.get_user("507f1f77bcf86cd799439011")

    async def test_list_users_pagination(self, mock_db, service):
        for i in range(5):
            await service.create_user(
                UserCreate(name=f"U{i}", email=f"u{i}@example.com")
            )
        users, total = await service.list_users(page=1, page_size=3)
        assert total == 5
        assert len(users) == 3


class TestUserServiceUpdate:
    async def test_update_user(self, mock_db, service):
        created = await service.create_user(
            UserCreate(name="Old", email="upd@example.com")
        )
        updated = await service.update_user(
            str(created.id), UserUpdate(name="New")
        )
        assert updated.name == "New"

    async def test_update_missing_raises(self, mock_db, service):
        with pytest.raises(EntityNotFoundError):
            await service.update_user(
                "507f1f77bcf86cd799439011", UserUpdate(name="Ghost")
            )


class TestUserServiceDelete:
    async def test_delete_user(self, mock_db, service):
        created = await service.create_user(
            UserCreate(name="Del", email="del@example.com")
        )
        await service.delete_user(str(created.id))
        with pytest.raises(EntityNotFoundError):
            await service.get_user(str(created.id))

    async def test_delete_missing_raises(self, mock_db, service):
        with pytest.raises(EntityNotFoundError):
            await service.delete_user("507f1f77bcf86cd799439011")
