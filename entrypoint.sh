#!/bin/sh
set -e

cd /app
alembic upgrade head

exec uvicorn app:app --host 0.0.0.0 --port "${APP_PORT:-8000}"
