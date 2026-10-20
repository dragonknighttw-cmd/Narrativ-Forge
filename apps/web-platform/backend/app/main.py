from collections import defaultdict, deque
import logging
from contextlib import asynccontextmanager
from time import monotonic, perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# Guard sentry import — optional dependency
try:
    from sentry_sdk.integrations.fastapi import FastApiIntegration as _FastApiIntegration
    _SENTRY_FASTAPI_INTEGRATION = _FastApiIntegration
except ImportError:
    _SENTRY_FASTAPI_INTEGRATION = None

from .core.config import settings
from .db import init_db
from .api.router import api_router
from .metrics import observe_http_metrics, router as metrics_router
from .observability import configure_logging, initialize_sentry

settings.validate_runtime()
configure_logging(settings.app_env)
_sentry_integrations = [_SENTRY_FASTAPI_INTEGRATION()] if _SENTRY_FASTAPI_INTEGRATION else []
initialize_sentry(
    settings.sentry_dsn.get_secret_value(),
    settings.app_env,
    integrations=_sentry_integrations,
)

request_logger = logging.getLogger("app.http")

# Rate limit windows: use deque for O(1) popleft instead of list O(n) filter
_rate_windows: dict[str, deque] = defaultdict(deque)
_RATE_LIMITS = {
    "login": (30, 60),
    "upload": (30, 60),
    "default": (300, 60),
}


@asynccontextmanager
async def lifespan(_: "FastAPI"):
    """Modern lifespan context manager — replaces deprecated @app.on_event."""
    init_db()
    yield


app = FastAPI(title="Narrativ Forge API", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def prometheus_http_metrics(request: Request, call_next):
    return await observe_http_metrics(request, call_next)


@app.middleware("http")
async def log_request(request: Request, call_next):
    started_at = perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        request_logger.error(
            "http_request",
            extra={
                "event": "http_request",
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": round((perf_counter() - started_at) * 1000, 2),
                "error_type": type(exc).__name__,
            },
        )
        raise

    request_logger.log(
        logging.ERROR if response.status_code >= 500 else logging.INFO,
        "http_request",
        extra={
            "event": "http_request",
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round((perf_counter() - started_at) * 1000, 2),
        },
    )
    return response

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.trusted_host_list,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Idempotency-Key"],
)


@app.middleware("http")
async def baseline_rate_limit(request: Request, call_next):
    path = request.url.path
    if path.endswith("/auth/login") or path.endswith("/auth/supabase-login"):
        bucket = "login"
    elif "/assets/upload" in path or path.startswith("/api/v1/uploads"):
        bucket = "upload"
    else:
        bucket = "default"
    limit, window = _RATE_LIMITS[bucket]
    key = f"{request.client.host if request.client else 'unknown'}:{bucket}"
    now = monotonic()
    dq = _rate_windows[key]
    # Evict expired entries from the left (deque is sorted oldest→newest)
    while dq and now - dq[0] >= window:
        dq.popleft()
    if len(dq) >= limit:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please retry later."},
            headers={"Retry-After": str(window)},
        )
    response = await call_next(request)
    # Count failed authentication attempts rather than successful logins so
    # the test suite and normal users do not exhaust the brute-force budget.
    if bucket == "login" and response.status_code in {401, 403}:
        dq.append(now)
    elif bucket != "login":
        dq.append(now)
    return response


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none';",
    )
    if settings.is_production:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


app.include_router(api_router, prefix="/api/v1")
app.include_router(metrics_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "narrativ-forge-api", "status": "ok"}

