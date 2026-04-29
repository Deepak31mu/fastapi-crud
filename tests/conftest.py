"""Shared pytest fixtures.

Uses mongomock-motor so tests run without a real MongoDB instance.
"""

import pytest
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.models.user import User


@pytest.fixture()
async def mock_db():
    """Initialise Beanie with an in-memory mock MongoDB."""
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client["test_db"],
        document_models=[User],
    )
    yield client
    client.close()


@pytest.fixture()
async def async_client(mock_db):
    """Provide an HTTPX AsyncClient wired to the FastAPI app.

    We import the app *after* the mock DB is initialised so that
    the Beanie document classes are already configured.
    """
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture()
def sample_user_payload() -> dict:
    """Return a valid user creation payload."""
    return {"name": "Test User", "email": "test@example.com"}


@pytest.fixture()
async def created_user(async_client, sample_user_payload) -> dict:
    """Create a user via the API and return the response body."""
    resp = await async_client.post("/api/v1/users/", json=sample_user_payload)
    assert resp.status_code == 201
    return resp.json()
