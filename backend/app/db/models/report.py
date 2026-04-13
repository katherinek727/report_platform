import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Report(Base):
    """Represents a registered report type available on the platform."""

    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    slug: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        index=True,
        comment="Machine-readable identifier used by the report registry",
    )
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="Human-readable display name",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="",
        comment="Short description shown in the UI",
    )
    output_format: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        comment="Output file format: xlsx | pdf",
    )

    runs: Mapped[list["ReportRun"]] = relationship(  # noqa: F821
        "ReportRun",
        back_populates="report",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Report slug={self.slug!r} format={self.output_format!r}>"
