#!/usr/bin/env sh
# Entrypoint for the Celery worker container.
# Concurrency is set to 2 — sufficient for a prototype.
# In production, tune --concurrency based on CPU count and I/O profile.
exec celery -A app.workers.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --queues=reports
