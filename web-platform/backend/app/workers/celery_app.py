from __future__ import annotations

from celery import Celery
from typing import Optional

from ..core.config import settings


def make_celery(broker_url: Optional[str] = None) -> Celery:
    """Create and return a Celery application.

    The function defers requiring settings.redis_url until the Celery app is
    actually created/used. This avoids import-time failures when Redis is not
    configured (for example during some test runs or fast imports).
    """

    broker = broker_url or settings.redis_url
    if not broker:
        raise RuntimeError("REDIS_URL must be configured to create the Celery broker")

    app = Celery("narrativ", broker=broker)
    # Minimal, safe configuration
    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=False,
    )
    return app


# Helper: safe factory that returns None if broker not configured
celery_app: Celery | None = None

def get_celery(allow_missing: bool = False) -> Optional[Celery]:
    global celery_app
    if celery_app is not None:
        return celery_app
    try:
        celery_app = make_celery()
        return celery_app
    except RuntimeError:
        if allow_missing:
            return None
        raise
