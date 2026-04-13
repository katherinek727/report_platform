import logging
import os
import uuid
from datetime import datetime, timezone

from app.db.models.report_run import ReportRun, RunStatus
from app.db.sync_engine import SyncSessionFactory
from app.reports.autodiscover import autodiscover_reports
from app.reports.registry import registry
from app.workers.celery_app import celery_app
from app.workers.transitions import assert_transition

logger = logging.getLogger(__name__)


def _ensure_registry() -> None:
    """Lazily populate the registry inside the worker process."""
    if len(registry) == 0:
        autodiscover_reports()


@celery_app.task(
    name="reports.generate",
    bind=True,
    max_retries=0,
    queue="reports",
)
def generate_report(self, run_id: str) -> dict:  # type: ignore[type-arg]
    """
    Core Celery task: generate a report for the given run_id.

    Lifecycle:
        PENDING → RUNNING → DONE | FAILED

    The task is intentionally kept thin — all generation logic lives
    in the report module itself. This task only handles:
      - Status transitions
      - Output path construction
      - Error capture and persistence
    """
    _ensure_registry()

    with SyncSessionFactory() as session:
        run: ReportRun | None = session.get(ReportRun, uuid.UUID(run_id))

        if run is None:
            logger.error("ReportRun %s not found — aborting task.", run_id)
            return {"status": "error", "detail": "run not found"}

        # Transition → RUNNING
        assert_transition(run.status, RunStatus.RUNNING)
        run.status = RunStatus.RUNNING
        run.started_at = datetime.now(timezone.utc)
        session.commit()

        try:
            report = registry.get(str(run.report.slug))
            output_dir = os.environ.get("STORAGE_PATH", "/storage")
            os.makedirs(output_dir, exist_ok=True)

            filename = f"{run.report.slug}_{run_id}.{report.meta.output_format}"
            output_path = os.path.join(output_dir, filename)

            report.generate(output_path=output_path)

            # Transition → DONE
            assert_transition(run.status, RunStatus.DONE)
            run.status = RunStatus.DONE
            run.result_path = filename
            run.finished_at = datetime.now(timezone.utc)
            session.commit()

            logger.info("Report run %s completed: %s", run_id, filename)
            return {"status": RunStatus.DONE, "result_path": filename}

        except Exception as exc:
            logger.exception("Report run %s failed.", run_id)

            assert_transition(run.status, RunStatus.FAILED)
            run.status = RunStatus.FAILED
            run.error_message = str(exc)
            run.finished_at = datetime.now(timezone.utc)
            session.commit()

            return {"status": RunStatus.FAILED, "error": str(exc)}
