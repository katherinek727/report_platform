"""
Sales Summary — Data Source
============================
Currently returns deterministic mock data.

In production, replace this module's implementation with a real
data source (e.g. SQLAlchemy query, internal REST API call, S3 file).
The interface — a function returning list[SalesRow] — must stay the same
so the generator and report class require zero changes.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SalesRow:
    month: str
    product: str
    region: str
    units_sold: int
    revenue_usd: float


def fetch_sales_data() -> list[SalesRow]:
    """
    Return sales data for the last 6 months.

    TODO (production): Replace with a parameterised DB query.
        SELECT month, product, region, SUM(units) AS units_sold,
               SUM(revenue) AS revenue_usd
        FROM   sales_facts
        WHERE  month >= NOW() - INTERVAL '6 months'
        GROUP  BY month, product, region
        ORDER  BY month, product, region
    """
    return [
        SalesRow("2024-01", "Widget Pro",   "North",  1_200, 48_000.00),
        SalesRow("2024-01", "Widget Pro",   "South",    980, 39_200.00),
        SalesRow("2024-01", "Gadget Lite",  "North",  2_300, 34_500.00),
        SalesRow("2024-01", "Gadget Lite",  "South",  1_750, 26_250.00),
        SalesRow("2024-02", "Widget Pro",   "North",  1_350, 54_000.00),
        SalesRow("2024-02", "Widget Pro",   "South",  1_100, 44_000.00),
        SalesRow("2024-02", "Gadget Lite",  "North",  2_500, 37_500.00),
        SalesRow("2024-02", "Gadget Lite",  "South",  1_900, 28_500.00),
        SalesRow("2024-03", "Widget Pro",   "North",  1_500, 60_000.00),
        SalesRow("2024-03", "Widget Pro",   "South",  1_250, 50_000.00),
        SalesRow("2024-03", "Gadget Lite",  "North",  2_700, 40_500.00),
        SalesRow("2024-03", "Gadget Lite",  "South",  2_100, 31_500.00),
        SalesRow("2024-04", "Widget Pro",   "North",  1_420, 56_800.00),
        SalesRow("2024-04", "Widget Pro",   "South",  1_180, 47_200.00),
        SalesRow("2024-04", "Gadget Lite",  "North",  2_600, 39_000.00),
        SalesRow("2024-04", "Gadget Lite",  "South",  2_050, 30_750.00),
        SalesRow("2024-05", "Widget Pro",   "North",  1_600, 64_000.00),
        SalesRow("2024-05", "Widget Pro",   "South",  1_300, 52_000.00),
        SalesRow("2024-05", "Gadget Lite",  "North",  2_800, 42_000.00),
        SalesRow("2024-05", "Gadget Lite",  "South",  2_200, 33_000.00),
        SalesRow("2024-06", "Widget Pro",   "North",  1_750, 70_000.00),
        SalesRow("2024-06", "Widget Pro",   "South",  1_450, 58_000.00),
        SalesRow("2024-06", "Gadget Lite",  "North",  3_000, 45_000.00),
        SalesRow("2024-06", "Gadget Lite",  "South",  2_400, 36_000.00),
    ]
