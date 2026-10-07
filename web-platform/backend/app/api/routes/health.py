from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import get_db

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    return {"status": "ok", "service": "narrativ-forge-api"}


@router.get("/ready")
def readiness(db: Session = Depends(get_db)):
    checks = {"database": "ok", "redis": "disabled"}
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        checks["database"] = "error"

    if settings.redis_url:
        try:
            import redis
            redis.Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1).ping()
            checks["redis"] = "ok"
        except Exception:
            checks["redis"] = "error"

    ready = checks["database"] == "ok" and checks["redis"] in {"ok", "disabled"}
    return {"status": "ready" if ready else "not_ready", "checks": checks}
