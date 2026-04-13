"""
Sales Summary Report
====================
Produces a monthly sales summary as an XLSX workbook.

Data source: mock (see data_source.py)
Output format: xlsx

To replace the mock with a real data source, implement the same
interface in data_source.py — the report class itself stays unchanged.
"""

from app.reports.base import BaseReport, ReportMeta
from app.reports.sales_summary.data_source import fetch_sales_data
from app.reports.sales_summary.generator import build_xlsx


class SalesSummaryReport(BaseReport):
    """Monthly sales summary broken down by product and region."""

    @property
    def meta(self) -> ReportMeta:
        return ReportMeta(
            slug="sales-summary",
            name="Sales Summary",
            description="Monthly sales breakdown by product and region (XLSX).",
            output_format="xlsx",
        )

    def generate(self, output_path: str) -> None:
        data = fetch_sales_data()
        build_xlsx(data=data, output_path=output_path)
