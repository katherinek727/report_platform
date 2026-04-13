"""
Status transition helpers for ReportRun.

Centralises all state-machine logic so that both the Celery task
and any future retry/cancel mechanisms use the same rules.

Valid transitions:
    PENDING  → RUNNING
    RUNNING  → DONE
    RUNNING  → FAILED

Any other transition raises InvalidTransitionError, making illegal
state changes loud and traceable rather than silently corrupted.
"""

from app.db.models.report_run import RunStatus

# Adjacency map: current_status → set of allowed next statuses
_ALLOWED: dict[str, set[str]] = {
    RunStatus.PENDING: {RunStatus.RUNNING},
    RunStatus.RUNNING: {RunStatus.DONE, RunStatus.FAILED},
    RunStatus.DONE: set(),
    RunStatus.FAILED: set(),
}


class InvalidTransitionError(Exception):
    """Raised when a status transition violates the state machine."""


def assert_transition(current: str, next_status: str) -> None:
    """
    Validate that transitioning from `current` to `next_status` is legal.

    Args:
        current:     The run's current status string.
        next_status: The desired next status string.

    Raises:
        InvalidTransitionError: If the transition is not permitted.
    """
    allowed = _ALLOWED.get(current, set())
    if next_status not in allowed:
        raise InvalidTransitionError(
            f"Cannot transition ReportRun from '{current}' to '{next_status}'. "
            f"Allowed transitions from '{current}': {allowed or 'none (terminal state)'}."
        )
