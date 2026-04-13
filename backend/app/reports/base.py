from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ReportMeta:
    """Static metadata that every report module must declare."""

    slug: str
    name: str
    description: str
    output_format: str  # "xlsx" | "pdf"


class BaseReport(ABC):
    """
    Abstract base class for all report implementations.

    To add a new report to the platform:
    1. Create a new module under app/reports/
    2. Subclass BaseReport
    3. Implement `meta` and `generate()`
    4. The registry will auto-discover it on startup

    The `generate()` method receives an output path and is responsible
    for writing the final file to that location. It runs inside a
    Celery worker, so blocking I/O is acceptable.
    """

    @property
    @abstractmethod
    def meta(self) -> ReportMeta:
        """Return static metadata describing this report."""
        ...

    @abstractmethod
    def generate(self, output_path: str) -> None:
        """
        Generate the report and write it to `output_path`.

        Args:
            output_path: Absolute path where the output file must be written.

        Raises:
            Exception: Any exception will be caught by the worker and
                       recorded as a failed run.
        """
        ...
