"""MongoDB connection management using Motor + Beanie ODM."""

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import get_settings
from app.models.user import User

_client: AsyncIOMotorClient | None = None


async def connect_to_database() -> None:
    """Initialise the MongoDB connection and Beanie ODM."""
    global _client
    settings = get_settings()
    _client = AsyncIOMotorClient(settings.mongodb_url)
    await init_beanie(
        database=_client[settings.mongodb_db_name],
        document_models=[User],
    )


async def close_database_connection() -> None:
    """Gracefully close the MongoDB connection."""
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_client() -> AsyncIOMotorClient | None:
    """Return the current Motor client (useful for health-checks)."""
    return _client
