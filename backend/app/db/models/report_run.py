import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class ReportRun(Base):
    """Represents a single execution of a report."""

    __tablename__ = "report_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=RunStatus.PENDING,
        index=True,
        comment="Current lifecycle status of this run",
    )
    result_path: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="Relative path to the generated file inside the storage volume",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Populated when status=failed",
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    report: Mapped["Report"] = relationship(  # noqa: F821
        "Report",
        back_populates="runs",
    )

    def __repr__(self) -> str:
        return f"<ReportRun id={self.id!s} status={self.status!r}>"
