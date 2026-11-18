"""
FastAPI application factory.

Creates and configures the FastAPI app with middleware, routers, static mounts, and lifecycle events.
"""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.health import router as health_router
from app.api.v1.sessions import router as sessions_router
from app.config import settings
from app.db.session import init_db
from app.services.demo_generator import ensure_demo_media

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan — startup and shutdown events."""
    logger.info(
        "Starting Video Intelligence Application",
        app_name=settings.app_name,
        environment=settings.app_env,
    )
    # Ensure storage paths exist
    for dir_path in [settings.storage_dir, settings.upload_dir, settings.keyframes_dir, settings.reports_dir, settings.demo_dir]:
        os.makedirs(dir_path, exist_ok=True)

    # Initialize SQLite / PostgreSQL tables automatically
    try:
        await init_db()
        logger.info("Database tables initialized successfully")
    except Exception as exc:
        logger.error("Failed to initialize database", error=str(exc))

    # Pre-generate demo media so the faculty demo is instant
    try:
        ensure_demo_media()
        logger.info("Faculty demo media verified and ready")
    except Exception as exc:
        logger.warning("Could not pre-generate demo media on startup", error=str(exc))

    yield

    logger.info("Shutting down Video Intelligence Application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        description="AI-Powered Meeting & Video Intelligence Report Generator",
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # --- Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Static Files Mount (Keyframes, Reports, Uploads) ---
    os.makedirs(settings.storage_dir, exist_ok=True)
    app.mount("/static", StaticFiles(directory=settings.storage_dir), name="static")

    # --- Routers ---
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(sessions_router, prefix="/api/v1")

    return app


# Application instance
app = create_app()
