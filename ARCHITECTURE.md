# Architecture

Report Platform — technical design, decisions, and developer guide.

---

## 1. System Overview

Report Platform is a service that lets developers register report modules,
users trigger their generation asynchronously, and download the results.

The core design constraint: **adding a new report should take less than a day**,
require no changes to platform code, and be safe to deploy independently.

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          Browser                                │
│                      React + TypeScript                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP (REST)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│                                                                 │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────────┐  │
│  │  /reports   │   │    /runs     │   │      /health        │  │
│  └──────┬──────┘   └──────┬───────┘   └─────────────────────┘  │
│         │                 │                                     │
│         └────────┬────────┘                                     │
│                  ▼                                              │
│         ┌────────────────┐                                      │
│         │  SQLAlchemy    │──────────────────► PostgreSQL        │
│         │  (async)       │                                      │
│         └────────────────┘                                      │
│                  │                                              │
│         ┌────────▼────────┐                                     │
│         │  Celery Task    │──────────────────► Redis (broker)   │
│         │  Dispatch       │                                      │
│         └─────────────────┘                                     │
└─────────────────────────────────────────────────────────────────┘
                           │ Task queue
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Celery Worker                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   generate_report task                   │   │
│  │                                                          │   │
│  │  1. Load ReportRegistry (auto-discovered on startup)     │   │
│  │  2. Transition run: PENDING → RUNNING                    │   │
│  │  3. Call report.generate(output_path)                    │   │
│  │  4. Transition run: RUNNING → DONE | FAILED              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                  │                                              │
│         ┌────────▼────────┐                                     │
│         │  Report Module  │                                     │
│         │  (BaseReport)   │──────────────────► /storage volume  │
│         └─────────────────┘                                     │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow: Trigger → Download

```
User clicks "Generate"
        │
        ▼
POST /api/v1/reports/{slug}/runs
        │
        ├─► Create ReportRun (status=PENDING) in PostgreSQL
        ├─► Dispatch generate_report.apply_async(run_id) to Redis
        └─► Return 202 { run_id, status: "pending" }

Frontend polls GET /api/v1/runs/{run_id} every 2s
        │
        ▼
Worker picks up task from Redis
        │
        ├─► Update run: status=RUNNING, started_at=now
        ├─► Call report.generate(output_path)
        ├─► Write file to /storage/{slug}_{run_id}.{format}
        └─► Update run: status=DONE, result_path=filename

Frontend detects status=DONE → shows Download button
        │
        ▼
GET /api/v1/runs/{run_id}/download
        │
        └─► Stream file from /storage volume
```

---

## 2. How to Add a New Report

This is the most important section for day-to-day development.

### Step 1 — Create the module directory

```
backend/app/reports/my_report/
├── __init__.py
├── report.py       ← BaseReport subclass
├── data_source.py  ← Data fetching logic
└── generator.py    ← File generation logic
```

### Step 2 — Implement the data source

```python
# data_source.py
from dataclasses import dataclass

@dataclass(frozen=True)
class MyRow:
    field_a: str
    field_b: int

def fetch_data() -> list[MyRow]:
    # Replace with real DB query, API call, or file read
    return [MyRow("example", 42)]
```

### Step 3 — Implement the generator

```python
# generator.py
from app.reports.my_report.data_source import MyRow

def build_xlsx(data: list[MyRow], output_path: str) -> None:
    # Use openpyxl, reportlab, or any library
    ...
```

### Step 4 — Implement BaseReport

```python
# report.py
from app.reports.base import BaseReport, ReportMeta
from app.reports.my_report.data_source import fetch_data
from app.reports.my_report.generator import build_xlsx

class MyReport(BaseReport):
    @property
    def meta(self) -> ReportMeta:
        return ReportMeta(
            slug="my-report",          # unique, kebab-case
            name="My Report",
            description="What this report shows.",
            output_format="xlsx",      # "xlsx" or "pdf"
        )

    def generate(self, output_path: str) -> None:
        data = fetch_data()
        build_xlsx(data=data, output_path=output_path)
```

### Step 5 — Export from `__init__.py`

```python
# __init__.py
from app.reports.my_report.report import MyReport
__all__ = ["MyReport"]
```

### Step 6 — Restart the backend

```bash
docker compose restart backend worker
```

The auto-discovery mechanism scans `app.reports.*` on startup, finds `MyReport`,
registers it, and upserts it into the database. It will appear in the UI immediately.

**No other files need to change.**

---

## 3. Architectural Decisions

### ADR-1: Report Registry Pattern (Plugin Architecture)

**Decision**: Reports are self-contained modules that implement a `BaseReport`
interface and are discovered automatically at startup.

**Alternatives considered**:
- **Database-driven configuration**: Store report definitions in the DB.
  Rejected — requires a UI to manage report metadata, adds operational overhead,
  and makes code review harder (report logic lives outside the codebase).
- **Explicit registration in a central file**: A `REPORTS = [SalesSummary(), ...]` list.
  Rejected — requires modifying platform code to add a report, violating the
  "one day from idea to production" goal.
- **Auto-discovery (chosen)**: Scan `app.reports.*` for `BaseReport` subclasses.
  Accepted — zero-friction addition, no platform changes required, discoverable
  via `git log` (each report is its own commit).

---

### ADR-2: Celery + Redis for Async Task Queue

**Decision**: Use Celery with Redis as both broker and result backend.

**Alternatives considered**:
- **FastAPI BackgroundTasks**: Simple but runs in the API process — no retry,
  no persistence, no worker scaling. Rejected for production use.
- **ARQ (async Redis Queue)**: Lighter than Celery, async-native. Considered
  seriously — would be a good choice for a greenfield async-only stack.
  Rejected here because Celery has broader ecosystem support and the report
  generation code is inherently synchronous (openpyxl, reportlab).
- **Celery + RabbitMQ**: More robust broker for high-throughput scenarios.
  Rejected for prototype — Redis is simpler to operate and sufficient at this scale.
- **Celery + Redis (chosen)**: Battle-tested, well-documented, supports retries,
  task routing, and monitoring (Flower). Redis doubles as cache if needed later.

---

### ADR-3: Async FastAPI + Sync Celery (Two Engine Strategy)

**Decision**: Maintain separate async (asyncpg) and sync (psycopg2) SQLAlchemy
engines — one for FastAPI, one for Celery workers.

**Alternatives considered**:
- **Single async engine everywhere**: Celery doesn't natively support async tasks
  without `asyncio.run()` wrappers, which adds complexity and risk.
- **Single sync engine everywhere**: Would require making FastAPI endpoints sync,
  losing the concurrency benefits of async I/O.
- **Two engines (chosen)**: Clean separation. FastAPI uses async for high
  concurrency. Celery uses sync because report generation is CPU/IO-bound and
  benefits from simplicity over async overhead.

---

### ADR-4: File Storage as Docker Volume (not Object Storage)

**Decision**: Generated files are written to a named Docker volume (`storage_data`)
shared between the `backend` and `worker` containers.

**Alternatives considered**:
- **S3 / object storage**: The correct production choice. Durable, scalable,
  CDN-friendly. Rejected for prototype — adds AWS credentials, SDK dependency,
  and operational complexity that obscures the platform's core design.
- **Database BLOB storage**: Rejected — poor performance for large files,
  bloats the DB.
- **Docker volume (chosen)**: Zero-config, works identically in dev and CI,
  makes the prototype runnable with a single command. The download endpoint
  is already abstracted behind a service layer — swapping to S3 requires
  changing only `download_run()` in `runs.py`.

---

### ADR-5: CSS Modules over CSS-in-JS

**Decision**: Use CSS Modules for component styling.

**Alternatives considered**:
- **Tailwind CSS**: Excellent DX, but requires build-time setup and produces
  verbose JSX. Rejected to keep the frontend dependency footprint minimal.
- **styled-components / Emotion**: Runtime CSS-in-JS. Rejected — adds bundle
  weight and runtime overhead for a prototype.
- **CSS Modules (chosen)**: Zero runtime cost, scoped by default, works with
  Vite out of the box, and keeps styles co-located with components.
  Design tokens in `globals.css` provide the system-level consistency.

---

## 4. What's Not Done (and Why)

### Authentication & Authorization
Not implemented. In production, every endpoint would require a JWT or session
token. The download endpoint in particular must verify the user owns the run.
**Recommended approach**: FastAPI dependency injection with OAuth2/JWT middleware.

### Report Parameters
Currently reports take no input parameters. In production, reports often need
date ranges, filters, or user-specific data. **Recommended approach**: Add a
`params: dict` argument to `BaseReport.generate()` and a request body to
`POST /reports/{slug}/runs`. Store params on the `ReportRun` model.

### File Retention & Cleanup
Generated files accumulate indefinitely. In production, implement a scheduled
Celery beat task that deletes files older than N days and marks runs as `expired`.

### Observability
No metrics, tracing, or structured logging beyond basic stdout. In production:
- **Metrics**: Prometheus + Grafana (Celery task duration, queue depth, error rate)
- **Tracing**: OpenTelemetry with Jaeger or Datadog
- **Structured logging**: Replace basicConfig with `structlog`

### Report Scheduling
No cron-style scheduling. In production, add Celery Beat with a `ScheduledRun`
model to support "run this report every Monday at 9am" use cases.

### Multi-format Output per Report
Each report currently produces one format. In production, a report could support
multiple formats (XLSX + PDF) with the format selected at trigger time.

### Test Coverage
No automated tests in this prototype. In production:
- Unit tests for each report's generator (mock data source, assert file structure)
- Integration tests for API endpoints (pytest + httpx + test DB)
- E2E tests for the trigger → poll → download flow (Playwright)

### Production Docker Images
The `docker-compose.yml` uses `target: development` for all services (hot reload,
dev dependencies). Production images should use `target: production`, pin image
digests, run as non-root users, and be built in CI.
