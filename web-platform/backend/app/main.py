from collections import defaultdict
from time import monotonic

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .core.config import settings
from .db import init_db
from .api.router import api_router

settings.validate_runtime()
app = FastAPI(title="Narrativ Forge API", version="0.1.0")

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
    elif "/assets/upload" in path:
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


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "narrativ-forge-api", "status": "ok"}
