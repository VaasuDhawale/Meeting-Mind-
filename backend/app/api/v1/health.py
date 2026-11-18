"""
Health check endpoint.

Used by Docker health checks, load balancers, and monitoring to verify
the API is running and can reach its dependencies.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    app_name: str
    environment: str
    timestamp: str
    database: str
    version: str = "0.1.0"


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the health status of the API and its dependencies.",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Check that the API is alive and can reach the database."""
    # Test database connectivity
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        app_name=settings.app_name,
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=db_status,
    )
