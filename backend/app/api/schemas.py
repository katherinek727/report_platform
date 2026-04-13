"""
Pydantic response schemas for all API endpoints.

Keeping schemas in one module avoids circular imports and makes
the API contract easy to find and review in one place.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# ── Reports ────────────────────────────────────────────────────────────────

class ReportSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    name: str
    description: str
    output_format: str
    created_at: datetime


class ReportListResponse(BaseModel):
    items: list[ReportSchema]
    total: int


# ── Report Runs ────────────────────────────────────────────────────────────

class ReportRunSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    report_id: uuid.UUID
    status: str
    result_path: str | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class RunListResponse(BaseModel):
    items: list[ReportRunSchema]
    total: int


class TriggerRunResponse(BaseModel):
    run_id: uuid.UUID
    status: str


# ── Errors ─────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
