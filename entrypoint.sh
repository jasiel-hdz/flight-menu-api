#!/bin/sh
set -e

cd /app

python - <<'PY'
import time

from sqlalchemy import text

from database import engine

for _ in range(30):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("database not ready")
PY

python - <<'PY'
from database import Base, engine
from core.flights import models as _flights  # noqa: F401
from core.menus import models as _menus  # noqa: F401

Base.metadata.create_all(bind=engine)
PY

exec uvicorn app:app --host 0.0.0.0 --port "${APP_PORT:-8000}"
