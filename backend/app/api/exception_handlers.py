"""
Global exception handlers for the FastAPI application.

Centralises error response formatting so every error — whether raised
by application code or by FastAPI itself — returns a consistent JSON
shape: { "detail": "..." }
"""

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Pass-through for HTTPExceptions — normalise to our error shape."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return 422 with a human-readable summary of validation errors."""
    errors = exc.errors()
    messages = [
        f"{' → '.join(str(loc) for loc in err['loc'])}: {err['msg']}"
        for err in errors
    ]
    detail = "; ".join(messages)
    logger.warning("Validation error on %s %s: %s", request.method, request.url, detail)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": detail},
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all for unexpected server errors — log and return 500."""
    logger.exception(
        "Unhandled exception on %s %s", request.method, request.url
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )
