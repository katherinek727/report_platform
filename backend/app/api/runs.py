import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import (
    RunListResponse,
    ReportRunSchema,
    TriggerRunResponse,
)
from app.core.config import settings
from app.db.models.report import Report
from app.db.models.report_run import ReportRun, RunStatus
from app.db.session import get_session

router = APIRouter(tags=["runs"])


@router.get(
    "/runs/{run_id}",
    response_model=ReportRunSchema,
    summary="Get a single run by ID",
)
async def get_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> ReportRunSchema:
    """Return the current state of a report run, including status and timestamps."""
    run = await session.get(ReportRun, run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run '{run_id}' not found.",
        )
    return ReportRunSchema.model_validate(run)


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


# MIME type map — extend as new output formats are added
_MIME_TYPES: dict[str, str] = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf":  "application/pdf",
}


@router.get(
    "/runs/{run_id}/download",
    summary="Download the generated report file",
    response_class=FileResponse,
)
async def download_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> FileResponse:
    """
    Stream the generated file for a completed run.

    Returns 404 if the run doesn't exist.
    Returns 409 if the run has not yet completed.
    Returns 410 if the file is missing from storage (e.g. purged).
    """
    run = await session.get(ReportRun, run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run '{run_id}' not found.",
        )

    if run.status != RunStatus.DONE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Run is not complete yet (status: {run.status}).",
        )

    if not run.result_path:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Result file path is not recorded for this run.",
        )

    file_path = os.path.join(settings.storage_path, run.result_path)
    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Result file no longer exists in storage.",
        )

    extension = run.result_path.rsplit(".", 1)[-1].lower()
    media_type = _MIME_TYPES.get(extension, "application/octet-stream")

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=run.result_path,
    )
