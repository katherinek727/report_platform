import logging
from typing import Iterator

from app.reports.base import BaseReport, ReportMeta

logger = logging.getLogger(__name__)


class ReportRegistry:
    """
    Central registry that maps report slugs to their implementations.

    Reports are registered either explicitly via `register()` or
    automatically via `autodiscover()`. The registry is a singleton
    accessed through the module-level `registry` instance.

    Usage:
        from app.reports.registry import registry

        # Register manually
        registry.register(MyReport())

        # Look up by slug
        report = registry.get("sales-summary")

        # Iterate all
        for report in registry.all():
            print(report.meta.slug)
    """

    def __init__(self) -> None:
        self._reports: dict[str, BaseReport] = {}

    def register(self, report: BaseReport) -> None:
        """Register a report instance. Raises if slug is already taken."""
        slug = report.meta.slug
        if slug in self._reports:
            raise ValueError(
                f"Report with slug '{slug}' is already registered. "
                "Each report must have a unique slug."
            )
        self._reports[slug] = report
        logger.info("Registered report: %s (%s)", slug, report.meta.output_format)

    def get(self, slug: str) -> BaseReport:
        """Return a report by slug. Raises KeyError if not found."""
        try:
            return self._reports[slug]
        except KeyError:
            raise KeyError(f"No report registered with slug '{slug}'.")

    def all(self) -> Iterator[BaseReport]:
        """Iterate over all registered reports."""
        yield from self._reports.values()

    def all_meta(self) -> list[ReportMeta]:
        """Return metadata for all registered reports."""
        return [r.meta for r in self._reports.values()]

    def __len__(self) -> int:
        return len(self._reports)

    def __contains__(self, slug: str) -> bool:
        return slug in self._reports


# Module-level singleton — import this everywhere
registry = ReportRegistry()
