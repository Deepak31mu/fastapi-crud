"""FastAPI application entry-point.

Run with:  poetry run uvicorn app.main:app --reload
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.users import router as users_router
from app.config import get_settings
from app.database import close_database_connection, connect_to_database, get_client
from app.exceptions.handlers import register_exception_handlers

settings = get_settings()

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown events."""
    logger.info("Connecting to MongoDB at %s …", settings.mongodb_url)
    await connect_to_database()
    logger.info("Connected — database: %s", settings.mongodb_db_name)
    yield
    logger.info("Shutting down — closing MongoDB connection …")
    await close_database_connection()


# ── App factory ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="FastAPI CRUD service with MongoDB — layered architecture",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ───────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ──────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(users_router, prefix="/api/v1")


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    client = get_client()
    db_status = "disconnected"
    if client is not None:
        try:
            await client.admin.command("ping")
            db_status = "connected"
        except Exception:
            db_status = "error"
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "app": settings.app_name,
        "database": db_status,
    }
