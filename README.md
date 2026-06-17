# deephold-app

Modernes Web-Frontend für die `deephold_db` Finanzmarktdatenbank.

## Stack

| Schicht       | Technologie                                      |
|---------------|--------------------------------------------------|
| Frontend      | Next.js 15 + React 19 + Tailwind + shadcn/ui     |
| Charts        | ECharts (Apache 2.0)                             |
| Backend       | FastAPI (Python 3.12)                            |
| Datenbank     | PostgreSQL 16 (via `deephold_db` package)        |
| Reverse Proxy | Caddy (optional, für Production)                 |
| Pkg Mgmt      | pip/venv (API) + Bun (Web)                       |

## Quickstart (Development)

Voraussetzung: `deephold_pg` läuft auf `localhost:5432`.

```bash
# 1. .env anlegen
cp .env.example .env

# 2. Dependencies installieren
make install

# 3. Zwei Terminals öffnen:
# Terminal 1 — API:
make dev-api

# Terminal 2 — Web:
make dev-web
```

- Web: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Docker (Production-like)

```bash
make up    # Startet api + web + caddy
make down  # Stoppt alles
```

## Struktur

```
deephold-app/
├── api/                    # FastAPI Backend
│   ├── src/deephold_api/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
├── web/                    # Next.js Frontend
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── Dockerfile
├── caddy/                  # Reverse Proxy Config
├── docker-compose.yml
├── Makefile
└── .env.example
```
