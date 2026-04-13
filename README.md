# Report Platform

A developer-friendly platform for building, running, and delivering reports at speed.
Designed around a single principle: from idea to production report in one working day.

## Overview

Report Platform provides a structured way to add new reports as isolated modules,
trigger their generation asynchronously, and deliver results to users in multiple
formats (XLSX, PDF, and beyond).

## Project Structure

```
report-platform/
├── backend/        # FastAPI application, Celery workers, report modules
├── frontend/       # React + TypeScript web interface
├── infra/          # Docker and infrastructure configuration
├── storage/        # Generated report files (runtime, not committed)
└── ARCHITECTURE.md # Architecture decisions and developer guide
```

## Quick Start

> Full setup instructions will be added once infrastructure is wired up.

```bash
# Clone the repository
git clone <repo-url>
cd report-platform

# Start all services
docker compose up --build
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Adding a New Report

See [ARCHITECTURE.md](./ARCHITECTURE.md) for a step-by-step guide on adding
a new report module to the platform.

## Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| Backend     | Python, FastAPI, SQLAlchemy       |
| Task Queue  | Celery, Redis                     |
| Database    | PostgreSQL                        |
| Frontend    | React, TypeScript, Vite           |
| Reports     | openpyxl (XLSX), ReportLab (PDF)  |
| Infra       | Docker, docker-compose            |

## License

MIT
