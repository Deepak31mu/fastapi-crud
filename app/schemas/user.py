"""Pydantic schemas for User request / response validation.

These are intentionally separate from the Beanie document model so the API
contract is decoupled from the persistence layer.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ── Request schemas ──────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    """Payload for creating a new user."""

    name: str = Field(..., min_length=1, max_length=100, examples=["Deepak Upadhyay"])
    email: EmailStr = Field(..., examples=["deepak@example.com"])

    model_config = ConfigDict(str_strip_whitespace=True)


class UserUpdate(BaseModel):
    """Payload for updating an existing user.  All fields are optional."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None)
    is_active: bool | None = Field(default=None)

    model_config = ConfigDict(str_strip_whitespace=True)


# ── Response schemas ─────────────────────────────────────────────────────────


class UserResponse(BaseModel):
    """Single-user response returned by the API."""

    id: str = Field(..., alias="_id")
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class UserListResponse(BaseModel):
    """Paginated list of users."""

    total: int
    page: int
    page_size: int
    users: list[UserResponse]
