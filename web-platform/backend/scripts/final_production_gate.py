import os
import subprocess
import sys
import urllib.request

failures = []

def require(name, value):
    if not value:
        failures.append(name)

require("APP_ENV=production", os.environ.get("APP_ENV") == "production")
require("DATABASE_URL", os.environ.get("DATABASE_URL"))
require("SESSION_SECRET", len(os.environ.get("SESSION_SECRET", "")) >= 32)
require("SESSION_COOKIE_SECURE=true", os.environ.get("SESSION_COOKIE_SECURE", "").lower() == "true")
require("CORS_ORIGINS", os.environ.get("CORS_ORIGINS"))
require("TRUSTED_HOSTS", os.environ.get("TRUSTED_HOSTS"))
require("OAUTH_ENCRYPTION_KEY", os.environ.get("OAUTH_ENCRYPTION_KEY"))

storage_provider = os.environ.get("STORAGE_PROVIDER", "").lower()
require("STORAGE_PROVIDER=b2", storage_provider == "b2")
if storage_provider == "b2":
    for name in ("B2_APPLICATION_KEY_ID", "B2_APPLICATION_KEY", "B2_BUCKET_NAME", "B2_REGION"):
        require(name, os.environ.get(name))
    try:
        require("B2_SIGNED_URL_EXPIRY_SECONDS", int(os.environ.get("B2_SIGNED_URL_EXPIRY_SECONDS", "0")) > 0)
    except ValueError:
        failures.append("B2_SIGNED_URL_EXPIRY_SECONDS")

def run_checked(args, name):
    try:
        return subprocess.run(args, check=True, capture_output=True, text=True, timeout=60)
    except Exception:
        failures.append(name)
        return None

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
    (["whisper", "--help"], "whisper"),
]:
    if os.environ.get("SKIP_MEDIA_TOOL_GATE", "").lower() != "true":
        run_checked(command, name)

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
    run_checked([sys.executable, "-m", "pytest", "web-platform/backend/tests/test_foundation.py", "-q"], "full E2E tests")

if failures:
    print("PRODUCTION GATE: BLOCKED")
    for item in failures:
        print(" - " + item)
    raise SystemExit(1)

print("PRODUCTION GATE: READY")
