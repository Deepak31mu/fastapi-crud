"""User document model for MongoDB (Beanie ODM)."""

from datetime import datetime, timezone

from beanie import Document
from pydantic import EmailStr, Field
from pymongo import ASCENDING, IndexModel


class User(Document):
    """MongoDB document representing a user."""

    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Unique email address")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
        indexes = [IndexModel([("email", ASCENDING)], unique=True)]

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Deepak Upadhyay",
                "email": "deepak@example.com",
                "is_active": True,
            }
        }
