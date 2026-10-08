from __future__ import annotations

import os
import subprocess
import sys
import urllib.request
from pathlib import Path

failures: list[str] = []


def require(name: str, value: bool) -> None:
    if not value:
        failures.append(name)


def run_checked(args: list[str], name: str):
    try:
        return subprocess.run(args, check=True, capture_output=True, text=True, timeout=60)
    except Exception:
        failures.append(name)
        return None


# Keep release configuration validation aligned with the application's own
# production runtime guard instead of duplicating provider-specific rules here.
backend_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_root))
try:
    from app.core.config import Settings

    try:
        Settings().validate_runtime()
    except Exception as exc:
        failures.append(f"runtime configuration: {exc}")
except Exception as exc:
    failures.append(f"runtime configuration import: {exc}")

require("APP_ENV=production", os.environ.get("APP_ENV", "").lower() == "production")
require("DATABASE_URL", bool(os.environ.get("DATABASE_URL")))
require("REDIS_URL", bool(os.environ.get("REDIS_URL")))
require("SESSION_SECRET", len(os.environ.get("SESSION_SECRET", "")) >= 32)
require("SESSION_COOKIE_SECURE=true", os.environ.get("SESSION_COOKIE_SECURE", "").lower() == "true")
require("CORS_ORIGINS", bool(os.environ.get("CORS_ORIGINS")))
require("TRUSTED_HOSTS", bool(os.environ.get("TRUSTED_HOSTS")))
require("OAUTH_ENCRYPTION_KEY", bool(os.environ.get("OAUTH_ENCRYPTION_KEY")))

storage_provider = os.environ.get("STORAGE_PROVIDER", "").lower()
require("supported STORAGE_PROVIDER", storage_provider in {"b2", "cloudinary", "hybrid"})
if storage_provider in {"b2", "hybrid"}:
    for name in ("B2_APPLICATION_KEY_ID", "B2_APPLICATION_KEY", "B2_BUCKET_NAME", "B2_REGION"):
        require(name, bool(os.environ.get(name)))
if storage_provider in {"cloudinary", "hybrid"}:
    for name in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"):
        require(name, bool(os.environ.get(name)))
if storage_provider == "hybrid":
    for name in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_STORAGE_BUCKET"):
        require(name, bool(os.environ.get(name)))

if os.environ.get("STORAGE_REPLICA_ENABLED", "").lower() == "true":
    replica = os.environ.get("STORAGE_REPLICA_PROVIDER", "").lower()
    require("supported STORAGE_REPLICA_PROVIDER", replica in {"b2", "cloudinary"})
    require("replica provider differs from primary", replica != storage_provider)

if os.environ.get("WHISPER_REMOTE_ENABLED", "true").lower() == "true":
    require("CLOUDFLARE_WHISPER_WORKER_URL", bool(os.environ.get("CLOUDFLARE_WHISPER_WORKER_URL")))
    require("CLOUDFLARE_WHISPER_SHARED_SECRET", bool(os.environ.get("CLOUDFLARE_WHISPER_SHARED_SECRET")))

current = run_checked([sys.executable, "-m", "alembic", "current"], "alembic current")
heads = run_checked([sys.executable, "-m", "alembic", "heads"], "alembic heads")
if current and heads:
    current_ids = {line.split()[0] for line in current.stdout.splitlines() if line.strip() and not line.startswith("INFO")}
    head_ids = {line.split()[0] for line in heads.stdout.splitlines() if line.strip() and not line.startswith("INFO")}
    if not head_ids or not current_ids.intersection(head_ids):
        failures.append("database migration is not at head")

for command, name in [
    (["ffmpeg", "-version"], "ffmpeg"),
    (["ffprobe", "-version"], "ffprobe"),
]:
    if os.environ.get("SKIP_MEDIA_TOOL_GATE", "").lower() != "true":
        run_checked(command, name)

if os.environ.get("WHISPER_REMOTE_ENABLED", "true").lower() != "true":
    run_checked(["whisper", "--help"], "whisper")

for script in ("web-platform/backend/scripts/backup_db.py", "web-platform/backend/scripts/restore_db.py"):
    if not os.path.isfile(script):
        failures.append(script)

api_url = os.environ.get("PRODUCTION_API_URL")
if api_url:
    try:
        body = urllib.request.urlopen(api_url.rstrip("/") + "/api/v1/health", timeout=10).read()
        if b'"status":"ok"' not in body.replace(b" ", b""):
            failures.append("production health")
    except Exception:
        failures.append("production health")

edge_url = os.environ.get("PRODUCTION_EDGE_URL")
if edge_url:
    try:
        body = urllib.request.urlopen(edge_url.rstrip("/") + "/api/v1/health", timeout=10).read()
        if b'"status":"ok"' not in body.replace(b" ", b""):
            failures.append("edge health")
    except Exception:
        failures.append("edge health")

if os.environ.get("RUN_E2E_GATE", "").lower() == "true":
    run_checked(
        [sys.executable, "-m", "pytest", "-m", "integration", "-q"],
        "backend integration tests",
    )

if failures:
    print("PRODUCTION GATE: BLOCKED")
    for item in failures:
        print(" - " + item)
    raise SystemExit(1)

print("PRODUCTION GATE: READY")
