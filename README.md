# Flight Menu API

REST API for managing flight meal menus (multi-language ES/EN).

## Stack

- Python 3.11+ (Docker images use 3.12)
- FastAPI + Pydantic v2
- SQLAlchemy 2.0 + PostgreSQL 16

## Layout

```
app.py              # FastAPI factory + router wiring
config.py           # Settings from env
database.py         # Engine, session, Base
dependencies.py     # Shared DI (db, settings)
core/
  schemas/          # Shared DTOs (pagination)
  health/           # Healthcheck
  auth/             # JWT login (security helpers + service + routes)
  flights/          # Flight validation
  menus/            # Menus + dishes (routes → services → repositories)
```

Each domain module follows: `routes.py` → `services.py` → `repositories.py` → `models.py`, with request/response schemas in `schemas.py`.

JWT helpers live in `core/auth/security.py` (no FastAPI/DB). `dependencies.get_current_user` protects menus and flights.

## Quick start (local / dev)

Runs PostgreSQL in Docker. The API runs on your machine.

### 1. Env

```bash
cp .env.example .env
```

`.env` defaults point the API to Postgres on `localhost:5435` (mapped by compose dev).

### 2. Database (Docker)

```bash
docker compose -f docker-compose.dev.yml up -d
```

Check it is healthy:

```bash
docker compose -f docker-compose.dev.yml ps
```

Stop / remove:

```bash
docker compose -f docker-compose.dev.yml down
# wipe data volume:
docker compose -f docker-compose.dev.yml down -v
```

### 3. API (host)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python app.py
# or: uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Open docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Health check:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

### Auth (JWT)

Default mock user comes from `.env` (`AUTH_USERNAME` / `AUTH_PASSWORD`).

```bash
# 1) Get a token
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# 2) Call a protected endpoint
curl -s http://127.0.0.1:8000/api/v1/menus \
  -H "Authorization: Bearer <access_token>"
```

In Swagger (`/docs`), use **Authorize** → Bearer token.

Public: `/health`, `/auth/login`, OpenAPI docs.  
Protected: `/menus/*`, `/flights/validate`.

---

## Production (API + DB with Docker)

`docker-compose.prod.yml` starts **both** PostgreSQL and the API. The API container waits for the DB, creates tables if needed, then serves on port `8000`.

### 1. Env

```bash
cp .env.example .env
```

Edit secrets in `.env` (`DB_PASSWORD`, etc.). Compose overrides `DB_HOST=postgres` and `DB_PORT=5432` inside the API container so it talks to the DB service on the Docker network.

### 2. Build and run

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Status:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f api
```

Health check:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

Stop:

```bash
docker compose -f docker-compose.prod.yml down
# wipe DB volume:
docker compose -f docker-compose.prod.yml down -v
```

### Services

| Service | Container | Host port | Notes |
|---------|-----------|-----------|--------|
| `postgres` | `flight-menu-postgres-prod` | (internal only) | Data in volume `postgres_flight_menu_prod` |
| `api` | `flight-menu-api-prod` | `8000` | Image built from `Dockerfile.prod` |

---

## Docker files

| File | Purpose |
|------|---------|
| `docker-compose.dev.yml` | Postgres only (dev). Host port **5435** |
| `docker-compose.prod.yml` | Postgres + API |
| `Dockerfile` | Dev image (optional; API usually runs on host in dev) |
| `Dockerfile.prod` | Production API image |
| `entrypoint.sh` | Wait for DB → create tables → uvicorn |

---

## Endpoints (`/api/v1`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Healthcheck |
| POST | `/auth/login` | No | Issue JWT access token |
| GET | `/menus` | Bearer | List menus (paginated) |
| POST | `/menus` | Bearer | Create menu |
| GET | `/menus/{id}` | Bearer | Menu detail with dishes |
| PUT | `/menus/{id}` | Bearer | Update menu |
| DELETE | `/menus/{id}` | Bearer | Soft delete |
| POST | `/menus/search` | Bearer | Filtered search |
| POST | `/flights/validate` | Bearer | Validate flight number + route |
