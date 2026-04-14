from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health(session: AsyncSession = Depends(get_session)) -> HealthResponse:
    """
    Returns service liveness status, version, and database connectivity.
    Used by docker-compose healthcheck and load balancers.
    """
    from app.core.config import settings

    db_status = "ok"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"

    return HealthResponse(
        status="ok",
        version=settings.app_version,
        database=db_status,
    )
