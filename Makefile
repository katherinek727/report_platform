.PHONY: up down build logs ps shell-backend shell-worker migrate reset

# ── Stack ──────────────────────────────────────────────────────────────────

up:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

ps:
	docker compose ps

# ── Database ───────────────────────────────────────────────────────────────

migrate:
	docker compose exec backend alembic upgrade head

migrate-down:
	docker compose exec backend alembic downgrade -1

# ── Shells ─────────────────────────────────────────────────────────────────

shell-backend:
	docker compose exec backend bash

shell-worker:
	docker compose exec worker bash

shell-db:
	docker compose exec postgres psql -U postgres -d reports

# ── Reset ──────────────────────────────────────────────────────────────────

reset:
	docker compose down -v --remove-orphans
	docker compose up --build -d
