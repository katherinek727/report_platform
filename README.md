# Report Platform

A developer-friendly platform for building, running, and delivering reports at speed.
Designed around a single principle: **from idea to production report in one working day.**

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url>
cd report-platform

# 2. Copy environment variables
cp .env.example .env

# 3. Start all services (one command)
docker compose up --build
```

That's it. The full stack will be available at:

| Service      | URL                          |
|--------------|------------------------------|
| Frontend     | http://localhost:5173        |
| Backend API  | http://localhost:8000        |
| API Docs     | http://localhost:8000/docs   |
| Health Check | http://localhost:8000/health |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) 24+
- [Docker Compose](https://docs.docker.com/compose/) v2+

No other dependencies required — everything runs inside containers.

## Project Structure

```
report-platform/
├── backend/                    # FastAPI application + Celery workers
│   ├── app/
│   │   ├── api/                # REST endpoints and schemas
│   │   ├── core/               # Config, logging
│   │   ├── db/                 # Models, engine, migrations
│   │   ├── reports/            # Report modules (registry + implementations)
│   │   │   ├── base.py         # Abstract BaseReport interface
│   │   │   ├── registry.py     # ReportRegistry singleton
│   │   │   ├── autodiscover.py # Auto-discovery on startup
│   │   │   ├── sales_summary/  # Report #1: XLSX
│   │   │   └── user_activity/  # Report #2: PDF
│   │   └── workers/            # Celery tasks and state machine
│   └── alembic/                # Database migrations
├── frontend/                   # React + TypeScript + Vite
│   └── src/
│       ├── api/                # Typed API client
│       ├── components/         # Shared UI components
│       ├── hooks/              # usePolling, useRunStatus
│       └── pages/              # ReportsList, RunsList, RunDetail
├── docker-compose.yml
├── Makefile                    # Dev shortcuts
├── .env.example
└── ARCHITECTURE.md             # Architecture decisions and developer guide
```

## Available Reports

| Slug             | Name             | Format | Description                              |
|------------------|------------------|--------|------------------------------------------|
| `sales-summary`  | Sales Summary    | XLSX   | Monthly sales breakdown by product/region |
| `user-activity`  | User Activity    | PDF    | Weekly user engagement metrics with charts |

## Adding a New Report

See [ARCHITECTURE.md](./ARCHITECTURE.md#how-to-add-a-new-report) for the full step-by-step guide.

The short version:

```bash
# 1. Create a new module
mkdir backend/app/reports/my_report

# 2. Implement BaseReport (see existing reports for reference)
# 3. Export the class from __init__.py
# 4. Restart the backend — it auto-discovers and seeds the new report
```

## Development Commands

```bash
make up           # Start all services
make down         # Stop all services
make logs         # Tail all logs
make ps           # Show service status
make migrate      # Run pending migrations
make shell-backend # Open a shell in the backend container
make reset        # Full reset (removes volumes)
```

## API Reference

| Method | Endpoint                        | Description                    |
|--------|---------------------------------|--------------------------------|
| GET    | `/health`                       | Service health + DB status     |
| GET    | `/api/v1/reports`               | List all available reports     |
| GET    | `/api/v1/reports/{slug}`        | Get report metadata            |
| POST   | `/api/v1/reports/{slug}/runs`   | Trigger a new run (async)      |
| GET    | `/api/v1/reports/{slug}/runs`   | List runs for a report         |
| GET    | `/api/v1/runs/{run_id}`         | Get run status                 |
| GET    | `/api/v1/runs/{run_id}/download`| Download generated file        |

Full interactive docs: http://localhost:8000/docs

## Tech Stack

| Layer       | Technology                              |
|-------------|-----------------------------------------|
| Backend     | Python 3.11, FastAPI, SQLAlchemy 2      |
| Task Queue  | Celery 5, Redis 7                       |
| Database    | PostgreSQL 16                           |
| Frontend    | React 18, TypeScript, Vite 5            |
| Reports     | openpyxl (XLSX), ReportLab (PDF)        |
| Infra       | Docker, docker-compose                  |

## License

MIT
