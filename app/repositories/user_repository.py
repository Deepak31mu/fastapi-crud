"""Concrete repository for User documents backed by MongoDB / Beanie."""

from datetime import UTC, datetime
from typing import Any

from beanie import PydanticObjectId

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data-access layer for User documents."""

    async def create(self, entity: User) -> User:
        await entity.insert()
        return entity

    async def get_by_id(self, entity_id: str) -> User | None:
        return await User.get(PydanticObjectId(entity_id))

    async def get_by_email(self, email: str) -> User | None:
        return await User.find_one(User.email == email)

    async def get_all(
        self, skip: int = 0, limit: int = 10, **filters: Any
    ) -> list[User]:
        query = User.find(filters) if filters else User.find()
        return await query.skip(skip).limit(limit).to_list()

    async def update(self, entity_id: str, update_data: dict[str, Any]) -> User | None:
        user = await self.get_by_id(entity_id)
        if user is None:
            return None
        update_data["updated_at"] = datetime.now(UTC)
        await user.update({"$set": update_data})
        # Refresh from DB to return the latest state
        return await self.get_by_id(entity_id)

    async def delete(self, entity_id: str) -> bool:
        user = await self.get_by_id(entity_id)
        if user is None:
            return False
        await user.delete()
        return True

    async def count(self, **filters: Any) -> int:
        if filters:
            return await User.find(filters).count()
        return await User.find().count()
