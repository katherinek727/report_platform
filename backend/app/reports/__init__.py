"""
Report modules available on the platform.

Each sub-package exposes a concrete BaseReport subclass.
The autodiscover mechanism scans this package on startup and
registers all non-abstract BaseReport subclasses automatically.

Available reports:
  - sales_summary   → SalesSummaryReport  (xlsx)
  - user_activity   → UserActivityReport  (pdf)
"""
