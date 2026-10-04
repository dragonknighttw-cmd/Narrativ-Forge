from collections import defaultdict
import logging
from time import monotonic, perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .core.config import settings
from .db import init_db
from .api.router import api_router
from .metrics import observe_http_metrics, router as metrics_router
from .observability import configure_logging, initialize_sentry

settings.validate_runtime()
configure_logging(settings.app_env)
initialize_sentry(
    settings.sentry_dsn.get_secret_value(),
    settings.app_env,
    integrations=[FastApiIntegration()],
)
app = FastAPI(title="Narrativ Forge API", version="0.1.0")
request_logger = logging.getLogger("app.http")


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
    allow_headers=["Content-Type", "Authorization"],
)

_rate_windows: dict[str, list[float]] = defaultdict(list)
_RATE_LIMITS = {
    "login": (30, 60),
    "upload": (30, 60),
    "default": (300, 60),
}


@app.middleware("http")
async def baseline_rate_limit(request: Request, call_next):
    path = request.url.path
    if path.endswith("/auth/login"):
        bucket = "login"
    elif "/assets/upload" in path or path.startswith("/api/v1/uploads"):
        bucket = "upload"
    else:
        bucket = "default"
    limit, window = _RATE_LIMITS[bucket]
    key = f"{request.client.host if request.client else 'unknown'}:{bucket}"
    now = monotonic()
    entries = [timestamp for timestamp in _rate_windows[key] if now - timestamp < window]
    if len(entries) >= limit:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please retry later."},
            headers={"Retry-After": str(window)},
        )
    entries.append(now)
    _rate_windows[key] = entries
    response = await call_next(request)
    return response


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if settings.is_production:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.on_event("startup")
def startup() -> None:
    init_db()


app.include_router(api_router, prefix="/api/v1")
app.include_router(metrics_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "narrativ-forge-api", "status": "ok"}
