from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.reports import router as reports_router
from app.api.runs import router as runs_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import AsyncSessionFactory
from app.reports.autodiscover import autodiscover_reports
from app.reports.seeder import seed_reports


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown logic."""
    configure_logging(debug=settings.debug)

    # Discover and register all report modules
    autodiscover_reports()

    # Sync registered reports to the database
    async with AsyncSessionFactory() as session:
        await seed_reports(session)

    yield

    # Shutdown (cleanup hooks go here)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(reports_router, prefix="/api/v1")
    app.include_router(runs_router, prefix="/api/v1")

    return app


app = create_app()
