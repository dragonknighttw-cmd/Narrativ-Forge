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

try:
    subprocess.run([sys.executable, "-m", "alembic", "current"], check=True, timeout=30)
except Exception:
    failures.append("alembic current")

api_url = os.environ.get("PRODUCTION_API_URL")
if api_url:
    try:
        body = urllib.request.urlopen(api_url.rstrip("/") + "/api/v1/health", timeout=10).read()
        if b'"status":"ok"' not in body.replace(b" ", b""):
            failures.append("production health")
    except Exception:
        failures.append("production health")

if failures:
    print("PRODUCTION GATE: BLOCKED")
    for item in failures:
        print(" - " + item)
    raise SystemExit(1)

print("PRODUCTION GATE: CONFIGURATION READY")
