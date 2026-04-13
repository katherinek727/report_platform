from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import ReportListResponse, ReportSchema
from app.db.models.report import Report
from app.db.session import get_session

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "",
    response_model=ReportListResponse,
    summary="List all available reports",
)
async def list_reports(
    session: AsyncSession = Depends(get_session),
) -> ReportListResponse:
    """Return all report types registered on the platform."""
    result = await session.execute(select(Report).order_by(Report.name))
    reports = result.scalars().all()

    return ReportListResponse(
        items=[ReportSchema.model_validate(r) for r in reports],
        total=len(reports),
    )


@router.get(
    "/{report_id}",
    response_model=ReportSchema,
    summary="Get a single report by ID",
)
async def get_report(
    report_id: str,
    session: AsyncSession = Depends(get_session),
) -> ReportSchema:
    """Return metadata for a single report type."""
    result = await session.execute(
        select(Report).where(Report.slug == report_id)
    )
    report = result.scalar_one_or_none()

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found.",
        )

    return ReportSchema.model_validate(report)
