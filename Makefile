# deephold-app — Makefile

SHELL := /bin/bash
.DEFAULT_GOAL := help

.PHONY: help
help: ## Zeige alle Targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Setup ------------------------------------------------------------------

.PHONY: install
install: install-api install-web ## Alle Dependencies installieren

.PHONY: install-api
install-api: ## API venv + deps installieren
	cd api && python3 -m venv .venv && \
	  .venv/bin/pip install --upgrade pip && \
	  .venv/bin/pip install -e ".[dev]" && \
	  .venv/bin/pip install -e ../finance_data

.PHONY: install-web
install-web: ## Web deps installieren (Bun)
	cd web && bun install

# --- Dev (native, hot reload) ----------------------------------------------

.PHONY: dev-api
dev-api: ## FastAPI dev server (hot reload, :8000)
	cd api && .venv/bin/uvicorn deephold_api.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: dev-web
dev-web: ## Next.js dev server (hot reload, :3000)
	cd web && bun run dev

# --- Docker -----------------------------------------------------------------

.PHONY: up
up: ## Docker Stack starten (api + web + caddy)
	docker compose up -d

.PHONY: down
down: ## Docker Stack stoppen
	docker compose down

.PHONY: logs
logs: ## Docker Logs (tail)
	docker compose logs -f --tail=200

.PHONY: ps
ps: ## Container-Status
	docker compose ps

# --- Test / Lint ------------------------------------------------------------

.PHONY: test
test: test-api test-web ## Alle Tests

.PHONY: test-api
test-api: ## API Tests (pytest)
	cd api && .venv/bin/pytest -v

.PHONY: test-web
test-web: ## Web Tests
	cd web && bun test

.PHONY: lint
lint: ## Ruff + ESLint
	cd api && .venv/bin/ruff check .
	cd web && bun run lint

.PHONY: format
format: ## Ruff format
	cd api && .venv/bin/ruff format .

.PHONY: typecheck
typecheck: ## TypeScript typecheck
	cd web && bun run typecheck
