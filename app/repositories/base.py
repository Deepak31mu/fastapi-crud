"""Abstract base repository defining the contract for data-access operations.

Every concrete repository must implement these methods, keeping the service
layer agnostic of the underlying data store.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Generic CRUD contract."""

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Persist a new entity and return it."""
        ...

    @abstractmethod
    async def get_by_id(self, entity_id: str) -> T | None:
        """Fetch a single entity by its primary key."""
        ...

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 10, **filters: Any) -> list[T]:
        """Return a paginated list of entities, optionally filtered."""
        ...

    @abstractmethod
    async def update(self, entity_id: str, update_data: dict[str, Any]) -> T | None:
        """Partially update an entity; return the updated entity or None."""
        ...

    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete an entity; return True if it existed."""
        ...

    @abstractmethod
    async def count(self, **filters: Any) -> int:
        """Return total count of entities matching the given filters."""
        ...
