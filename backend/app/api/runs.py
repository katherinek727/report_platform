import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    RunListResponse,
    ReportRunSchema,
    TriggerRunResponse,
)
from app.db.models.report import Report
from app.db.models.report_run import ReportRun, RunStatus
from app.db.session import get_session

router = APIRouter(tags=["runs"])


@router.post(
    "/reports/{report_slug}/runs",
    response_model=TriggerRunResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a new report generation run",
)
async def trigger_run(
    report_slug: str,
    session: AsyncSession = Depends(get_session),
) -> TriggerRunResponse:
    """
    Create a new ReportRun record in PENDING state and dispatch
    the generation task to the Celery worker queue.

    Returns immediately with the run_id so the client can poll status.
    """
    # Resolve report
    result = await session.execute(
        select(Report).where(Report.slug == report_slug)
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_slug}' not found.",
        )

    # Create run record
    run = ReportRun(
        id=uuid.uuid4(),
        report_id=report.id,
        status=RunStatus.PENDING,
    )
    session.add(run)
    await session.flush()  # get the ID before commit

    run_id = str(run.id)

    # Dispatch async task — import here to avoid circular imports at module load
    from app.workers.tasks import generate_report
    generate_report.apply_async(args=[run_id], task_id=run_id)

    await session.commit()

    return TriggerRunResponse(run_id=run.id, status=RunStatus.PENDING)


@router.get(
    "/reports/{report_slug}/runs",
    response_model=RunListResponse,
    summary="List all runs for a report",
)
async def list_runs(
    report_slug: str,
    session: AsyncSession = Depends(get_session),
) -> RunListResponse:
    """Return all runs for a given report, newest first."""
    result = await session.execute(
        select(Report).where(Report.slug == report_slug)
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_slug}' not found.",
        )

    runs_result = await session.execute(
        select(ReportRun)
        .where(ReportRun.report_id == report.id)
        .order_by(ReportRun.created_at.desc())
    )
    runs = runs_result.scalars().all()

    return RunListResponse(
        items=[ReportRunSchema.model_validate(r) for r in runs],
        total=len(runs),
    )
