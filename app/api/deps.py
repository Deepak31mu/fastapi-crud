"""Dependency-injection providers for FastAPI.

Using FastAPI's `Depends()` system keeps the router thin and makes it
trivial to swap implementations (e.g. in tests).
"""

from fastapi import Depends

from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


def get_user_repository() -> UserRepository:
    """Provide a UserRepository instance."""
    return UserRepository()


def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    """Provide a UserService wired to a UserRepository."""
    return UserService(repository=repo)
