FROM python:3.11-slim AS base

# Prevents Python from writing .pyc files and buffers stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# ── deps layer (cached unless pyproject.toml changes) ──────────────────────
FROM base AS deps

RUN pip install hatchling
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# ── development image ───────────────────────────────────────────────────────
FROM deps AS development

COPY pyproject.toml .
RUN pip install --no-cache-dir ".[dev]"
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── production image ────────────────────────────────────────────────────────
FROM deps AS production

COPY . .
# Ensure worker entrypoint is executable
RUN chmod +x worker.sh

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
