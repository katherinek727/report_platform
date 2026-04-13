import importlib
import inspect
import logging
import pkgutil

import app.reports as reports_pkg
from app.reports.base import BaseReport
from app.reports.registry import registry

logger = logging.getLogger(__name__)


def autodiscover_reports() -> None:
    """
    Scan all sub-modules of `app.reports` and auto-register any
    concrete subclass of BaseReport found within them.

    Convention: each report lives in its own sub-package, e.g.
        app/reports/sales_summary/report.py

    This function is called once during application startup so that
    adding a new report requires zero changes outside the report's
    own module — just drop it in and it appears on the platform.
    """
    package_path = reports_pkg.__path__
    package_name = reports_pkg.__name__

    for _finder, module_name, _is_pkg in pkgutil.walk_packages(
        path=package_path,
        prefix=f"{package_name}.",
        onerror=lambda name: logger.warning("Failed to import %s", name),
    ):
        # Skip internal modules
        if module_name.endswith(("base", "registry", "autodiscover")):
            continue

        try:
            module = importlib.import_module(module_name)
        except Exception:
            logger.exception("Error importing report module: %s", module_name)
            continue

        for _attr_name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, BaseReport)
                and obj is not BaseReport
                and not inspect.isabstract(obj)
            ):
                slug = obj().meta.slug
                if slug not in registry:
                    registry.register(obj())

    logger.info("Auto-discovery complete. %d report(s) registered.", len(registry))
