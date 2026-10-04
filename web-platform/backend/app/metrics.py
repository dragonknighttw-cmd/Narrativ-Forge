from __future__ import annotations

import logging
from datetime import datetime, timezone
from threading import Lock
from time import perf_counter

from fastapi import APIRouter, HTTPException, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily, HistogramMetricFamily
from redis import Redis
from sqlalchemy import case, func, or_, select

from . import db
from .core.config import settings
from .models import ProcessingJob

logger = logging.getLogger(__name__)
router = APIRouter(tags=["metrics"])

METRICS_KEY = "narrativ:prometheus:processing:v1"
DURATION_BUCKETS = (0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 300, 900, 3600)
JOB_STATES = ("started", "completed", "failed", "retry", "dlq")
JOB_OUTCOMES = ("completed", "failed", "retry", "dlq")

registry = CollectorRegistry()
_redis_client: Redis | None = None
_redis_client_lock = Lock()
http_requests = Counter(
    "narrativ_http_requests",
    "HTTP requests handled by this API process.",
    ("method", "route", "status"),
    registry=registry,
)
http_request_duration = Histogram(
    "narrativ_http_request_duration_seconds",
    "HTTP request duration handled by this API process.",
    ("method", "route", "status"),
    registry=registry,
)


def _warn_metrics_failure(exc: Exception) -> None:
    logger.warning("Metrics operation failed (%s)", type(exc).__name__)


def _shared_metrics_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        with _redis_client_lock:
            if _redis_client is None:
                if not settings.redis_url:
                    raise RuntimeError("REDIS_URL must be configured for shared worker metrics")
                _redis_client = Redis.from_url(
                    settings.redis_url,
                    protocol=2,
                    socket_connect_timeout=1,
                    socket_timeout=1,
                )
    return _redis_client


def _normalized_method(method: str) -> str:
    method = method.upper()
    return method if method in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"} else "OTHER"


def record_http_request(method: str, route: str, status_code: int, duration_seconds: float) -> None:
    try:
        bounded_route = route if route.startswith("/") and "?" not in route else "unmatched"
        status = f"{status_code // 100}xx" if 100 <= status_code < 600 else "other"
        labels = (_normalized_method(method), bounded_route, status)
        http_requests.labels(*labels).inc()
        http_request_duration.labels(*labels).observe(duration_seconds)
    except Exception as exc:
        _warn_metrics_failure(exc)


def record_processing_started() -> None:
    _update_worker_metrics((("counter", "started", 1),))


def record_processing_finished(
    outcome: str,
    duration_seconds: float,
    *,
    timed_out: bool = False,
) -> None:
    try:
        if outcome not in JOB_OUTCOMES:
            outcome = "failed"

        updates: list[tuple[str, str, float | int]] = [
            ("counter", outcome, 1),
            ("histogram_count", outcome, 1),
            ("histogram_sum", outcome, max(0.0, duration_seconds)),
        ]
        if timed_out:
            updates.append(("counter", "timeout", 1))
        updates.extend(
            ("histogram_bucket", f"{outcome}|{_bucket_key(bound)}", 1)
            for bound in DURATION_BUCKETS
            if duration_seconds <= bound
        )
        updates.append(("histogram_bucket", f"{outcome}|+Inf", 1))
        _update_worker_metrics(updates)
    except Exception as exc:
        _warn_metrics_failure(exc)


def _bucket_key(bound: float) -> str:
    return str(bound)


def _update_worker_metrics(updates: tuple[tuple[str, str, float | int], ...] | list[tuple[str, str, float | int]]) -> None:
    try:
        client = _shared_metrics_client()
        pipeline = client.pipeline(transaction=True)
        for operation, key, value in updates:
            field = f"{operation}|{key}"
            if operation == "histogram_sum":
                pipeline.hincrbyfloat(METRICS_KEY, field, value)
            else:
                pipeline.hincrby(METRICS_KEY, field, int(value))
        pipeline.execute()
    except Exception as exc:
        _warn_metrics_failure(exc)


def _decode_hash(raw: dict[bytes | str, bytes | str]) -> dict[str, str]:
    return {
        key.decode() if isinstance(key, bytes) else key:
        value.decode() if isinstance(value, bytes) else value
        for key, value in raw.items()
    }


class ProcessingMetricsCollector:
    def describe(self):
        return []

    def collect(self):
        client = _shared_metrics_client()
        values = _decode_hash(client.hgetall(METRICS_KEY))

        jobs = CounterMetricFamily(
            "narrativ_processing_jobs",
            "Real-processing lifecycle events observed by workers.",
            labels=["status"],
        )
        for state in JOB_STATES:
            count = int(values.get(f"counter|{state}", "0"))
            if count:
                jobs.add_metric([state], count)
        yield jobs

        timeouts = CounterMetricFamily(
            "narrativ_processing_timeouts",
            "Real-processing commands that exceeded their configured timeout.",
        )
        timeout_count = int(values.get("counter|timeout", "0"))
        if timeout_count:
            timeouts.add_metric([], timeout_count)
        yield timeouts

        durations = HistogramMetricFamily(
            "narrativ_processing_duration_seconds",
            "Time spent in the real-processing operation.",
            labels=["outcome"],
        )
        for outcome in JOB_OUTCOMES:
            count = int(values.get(f"histogram_count|{outcome}", "0"))
            if not count:
                continue
            buckets = [
                (
                    _bucket_key(bound),
                    int(values.get(f"histogram_bucket|{outcome}|{_bucket_key(bound)}", "0")),
                )
                for bound in DURATION_BUCKETS
            ]
            buckets.append(
                ("+Inf", int(values.get(f"histogram_bucket|{outcome}|+Inf", "0")))
            )
            total = float(values.get(f"histogram_sum|{outcome}", "0"))
            durations.add_metric([outcome], buckets, total)
        yield durations

        queue_depth = GaugeMetricFamily(
            "narrativ_job_queue_depth",
            "Real-processing jobs currently queued in the database.",
            labels=["schedule"],
        )
        now = datetime.now(timezone.utc)
        due = or_(ProcessingJob.next_run_at.is_(None), ProcessingJob.next_run_at <= now)
        statement = select(
            func.sum(case((due, 1), else_=0)),
            func.sum(case((ProcessingJob.next_run_at > now, 1), else_=0)),
        ).where(
            ProcessingJob.job_type == "real_processing",
            ProcessingJob.status == "queued",
        )
        with db.SessionLocal() as session:
            due_count, scheduled_count = session.execute(statement).one()
        queue_depth.add_metric(["due"], int(due_count or 0))
        queue_depth.add_metric(["scheduled"], int(scheduled_count or 0))
        yield queue_depth

registry.register(ProcessingMetricsCollector())


@router.get("/metrics", include_in_schema=False)
def metrics_endpoint() -> Response:
    try:
        return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
    except Exception as exc:
        _warn_metrics_failure(exc)
        raise HTTPException(status_code=503, detail="Metrics temporarily unavailable") from exc


async def observe_http_metrics(request: Request, call_next):
    started = perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        if request.url.path != "/metrics":
            route = getattr(request.scope.get("route"), "path", "unmatched")
            record_http_request(
                request.method,
                route,
                status_code,
                perf_counter() - started,
            )
