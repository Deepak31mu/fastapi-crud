"""Business-logic layer for User operations.

The service sits between the API router and the repository.  It enforces
business rules (e.g. duplicate-email checks) and maps between schemas
and domain models so that neither the router nor the repository needs
to know about the other's data structures.
"""

import logging
from typing import Any

from app.exceptions.handlers import DuplicateEntityError, EntityNotFoundError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Orchestrates user-related business logic."""

    def __init__(self, repository: UserRepository) -> None:
        self._repo = repository

    # ── Create ───────────────────────────────────────────────────────────────

    async def create_user(self, payload: UserCreate) -> User:
        """Create a new user after validating uniqueness of email."""
        existing = await self._repo.get_by_email(payload.email)
        if existing is not None:
            raise DuplicateEntityError(
                entity="User", field="email", value=payload.email
            )
        user = User(**payload.model_dump())
        created = await self._repo.create(user)
        logger.info("Created user id=%s email=%s", created.id, created.email)
        return created

    # ── Read ─────────────────────────────────────────────────────────────────

    async def get_user(self, user_id: str) -> User:
        """Get a single user by ID or raise 404."""
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise EntityNotFoundError(entity="User", entity_id=user_id)
        return user

    async def list_users(
        self, page: int = 1, page_size: int = 10, **filters: Any
    ) -> tuple[list[User], int]:
        """Return a page of users and the total count."""
        skip = (page - 1) * page_size
        users = await self._repo.get_all(skip=skip, limit=page_size, **filters)
        total = await self._repo.count(**filters)
        return users, total

    # ── Update ───────────────────────────────────────────────────────────────

    async def update_user(self, user_id: str, payload: UserUpdate) -> User:
        """Partially update a user."""
        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_user(user_id)

        # If email is being changed, check for duplicates
        if "email" in update_data:
            existing = await self._repo.get_by_email(update_data["email"])
            if existing is not None and str(existing.id) != user_id:
                raise DuplicateEntityError(
                    entity="User", field="email", value=update_data["email"]
                )

        updated = await self._repo.update(user_id, update_data)
        if updated is None:
            raise EntityNotFoundError(entity="User", entity_id=user_id)
        logger.info("Updated user id=%s", user_id)
        return updated

    # ── Delete ───────────────────────────────────────────────────────────────

    async def delete_user(self, user_id: str) -> None:
        """Delete a user by ID."""
        deleted = await self._repo.delete(user_id)
        if not deleted:
            raise EntityNotFoundError(entity="User", entity_id=user_id)
        logger.info("Deleted user id=%s", user_id)
