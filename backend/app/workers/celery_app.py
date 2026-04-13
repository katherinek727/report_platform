from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "report_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Reliability
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    # Result expiry — keep results for 24 hours
    result_expires=86400,
    # Retry policy for broker connection on startup
    broker_connection_retry_on_startup=True,
)
