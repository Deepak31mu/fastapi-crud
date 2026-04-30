"""User CRUD endpoints (API v1).

This module is the *thin controller* — it validates input via Pydantic
schemas, delegates to the service layer, and maps domain objects to
response schemas.  No business logic lives here.
"""

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_user_service
from app.schemas.user import UserCreate, UserListResponse, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


# ── Helpers ──────────────────────────────────────────────────────────────────


def _to_response(user) -> UserResponse:
    """Convert a Beanie User document to a UserResponse schema."""
    return UserResponse(
        _id=str(user.id),
        name=user.name,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


# ── Endpoints ────────────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await service.create_user(payload)
    return _to_response(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await service.get_user(user_id)
    return _to_response(user)


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List users with pagination",
)
async def list_users(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    service: UserService = Depends(get_user_service),
) -> UserListResponse:
    users, total = await service.list_users(page=page, page_size=page_size)
    return UserListResponse(
        total=total,
        page=page,
        page_size=page_size,
        users=[_to_response(u) for u in users],
    )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Partially update a user",
)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await service.update_user(user_id, payload)
    return _to_response(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> None:
    await service.delete_user(user_id)
