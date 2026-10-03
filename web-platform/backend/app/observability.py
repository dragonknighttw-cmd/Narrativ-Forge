from datetime import datetime, timezone
import json
import logging
import sys
from typing import Any

import sentry_sdk


_STRUCTURED_FIELDS = (
    "event",
    "method",
    "path",
    "status_code",
    "duration_ms",
    "error_type",
)


class UvicornAccessQueryFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        if isinstance(args, tuple) and len(args) >= 3 and isinstance(args[2], str):
            record.args = (*args[:2], args[2].partition("?")[0], *args[3:])
        return True


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in _STRUCTURED_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(app_env: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler._narrativ_structured_handler = True
    if app_env.lower() in {"production", "staging"}:
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))

    root_logger = logging.getLogger()
    root_logger.handlers[:] = [
        existing
        for existing in root_logger.handlers
        if not getattr(existing, "_narrativ_structured_handler", False)
    ]
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)

    access_logger = logging.getLogger("uvicorn.access")
    if not any(isinstance(item, UvicornAccessQueryFilter) for item in access_logger.filters):
        access_logger.addFilter(UvicornAccessQueryFilter())


def initialize_sentry(
    dsn: str,
    app_env: str,
    *,
    integrations: list[Any] | None = None,
) -> bool:
    if not dsn or app_env.lower() not in {"production", "staging"}:
        return False

    sentry_sdk.init(
        dsn=dsn,
        environment=app_env.lower(),
        integrations=integrations or [],
        send_default_pii=False,
        traces_sample_rate=0.0,
    )
    return True
