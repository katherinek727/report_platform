"""
User Activity Report
====================
Produces a user engagement summary as a PDF with charts and infographics.

Data source: mock (see data_source.py)
Output format: pdf

To replace the mock with a real data source, implement the same
interface in data_source.py — the report class itself stays unchanged.
"""

from app.reports.base import BaseReport, ReportMeta
from app.reports.user_activity.data_source import fetch_user_activity_data
from app.reports.user_activity.generator import build_pdf


class UserActivityReport(BaseReport):
    """Weekly user activity report with engagement metrics and charts."""

    @property
    def meta(self) -> ReportMeta:
        return ReportMeta(
            slug="user-activity",
            name="User Activity",
            description="Weekly user engagement metrics with charts (PDF).",
            output_format="pdf",
        )

    def generate(self, output_path: str) -> None:
        data = fetch_user_activity_data()
        build_pdf(data=data, output_path=output_path)
