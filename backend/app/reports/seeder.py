import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.report import Report
from app.reports.registry import registry

logger = logging.getLogger(__name__)


async def seed_reports(session: AsyncSession) -> None:
    """
    Upsert all registered reports into the database.

    Called once on application startup after auto-discovery.
    Ensures the DB stays in sync with the code — new reports appear
    automatically, and metadata changes (name, description) are applied.

    Note: Reports are never deleted here. Removing a report module
    will leave its DB row intact (preserving run history) but it will
    no longer be discoverable via the registry.
    """
    for report in registry.all():
        meta = report.meta

        result = await session.execute(
            select(Report).where(Report.slug == meta.slug)
        )
        existing = result.scalar_one_or_none()

        if existing is None:
            session.add(
                Report(
                    slug=meta.slug,
                    name=meta.name,
                    description=meta.description,
                    output_format=meta.output_format,
                )
            )
            logger.info("Seeded new report: %s", meta.slug)
        else:
            existing.name = meta.name
            existing.description = meta.description
            existing.output_format = meta.output_format
            logger.debug("Updated report metadata: %s", meta.slug)

    await session.commit()
    logger.info("Report seeding complete.")
