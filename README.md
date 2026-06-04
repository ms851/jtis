# JTIS — Judo Tournament Information System

Modulare SaaS-Software für die Organisation von Sport-Veranstaltungen.

## Tech Stack

| Layer | Technologie |
|-------|------------|
| Backend | Python 3.12+ / FastAPI |
| ORM | SQLAlchemy 2.x + Alembic |
| Frontend | React 18 + TypeScript + Vite |
| UI | react-bootstrap 5 |
| Auth | Keycloak (OIDC) |
| DB | PostgreSQL 16 (Row-Level Security) |
| Infra | Docker Compose |

## Quick Start (Development)

```bash
# Start all services
cd docker
docker compose up -d

# Backend läuft auf http://localhost:8000
# Frontend auf http://localhost:5173
# Keycloak auf http://localhost:8080
# API Docs: http://localhost:8000/docs
```

## Migrations

```bash
cd backend
alembic upgrade head
```

## Tests

```bash
# Backend
cd backend
pip install -r requirements.txt
pytest -v

# Frontend
cd frontend
npm ci
npm test
```

## Production

```bash
cd docker
docker compose -f docker-compose.prod.yml up -d
```

## Projektstruktur

```
/backend/          — Python FastAPI Backend
/frontend/         — React 18 + TypeScript Frontend
/docker/           — Docker Compose (Dev + Prod)
/docs/             — Konzept & Dokumentation
/.github/workflows — CI/CD Pipelines
```

## Module

| Nr | Modul | Phase |
|----|-------|-------|
| 0 | Event-Einstellungen | 1 ✅ |
| 1 | Helfer-/Personalplanung | 2 |
| 2 | Venue-Management | 3 |
| 3 | Transport-Management | 4 |
| 4 | Kommunikation | Post-MVP |
| 5 | Aufgabenmanagement | Post-MVP |
| 6 | Finanz-Controlling | Post-MVP |
| 7 | Hotel-Management | Post-MVP |

## API

- REST API mit OpenAPI (auto-generated)
- `/api/v1/health` — Health Check
- `/api/v1/events` — Event-Management
- `/api/v1/org` — Organisations-Einstellungen
- `/api/v1/admin` — SaaS-Administration
- `/api/v1/rbac` — Rollen & Rechte
- `/api/v1/users` — Benutzer & DSGVO

## Lizenz

Proprietär — © 2026
