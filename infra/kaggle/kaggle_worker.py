"""Bootstrap a one-job Narrativ Forge worker inside a Kaggle kernel."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from kaggle_secrets import UserSecretsClient

REPO = "dragonknighttw-cmd/Narrativ-Forge"
ROOT = Path("/kaggle/working/Narrativ-Forge")
TARGET_GIT_SHA = None  # Injected by dispatch.py before the kernel is pushed.

def secret(name: str, *, required: bool = True) -> str:
    value = UserSecretsClient().get_secret(name)
    if required and not value:
        raise RuntimeError(f"Missing Kaggle Secret: {name}")
    return value or ""

def main() -> None:
    database_url = secret("DATABASE_URL")
    if not TARGET_GIT_SHA or len(TARGET_GIT_SHA) != 40 or any(c not in "0123456789abcdef" for c in TARGET_GIT_SHA):
        raise RuntimeError("Kaggle dispatch did not provide a valid pinned Git commit SHA.")
    if ROOT.exists():
        subprocess.run(["rm", "-rf", str(ROOT)], check=True)
    git_env = os.environ.copy()
    git_env["GIT_TERMINAL_PROMPT"] = "0"
    subprocess.run(
        ["git", "clone", "--no-checkout", "--depth", "1", f"https://github.com/{REPO}.git", str(ROOT)],
        check=True,
        stdout=subprocess.DEVNULL,
        env=git_env,
    )
    subprocess.run(
        ["git", "-C", str(ROOT), "fetch", "--depth", "1", "origin", TARGET_GIT_SHA],
        check=True,
        stdout=subprocess.DEVNULL,
        env=git_env,
    )
    subprocess.run(
        ["git", "-C", str(ROOT), "checkout", "--detach", TARGET_GIT_SHA],
        check=True,
        stdout=subprocess.DEVNULL,
        env=git_env,
    )
    actual_sha = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    if actual_sha != TARGET_GIT_SHA:
        raise RuntimeError("Kaggle worker checkout did not match the requested commit SHA.")
    backend = ROOT / "apps/web-platform" / "backend"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    env.setdefault("APP_ENV", "production")
    storage_provider = secret("STORAGE_PROVIDER").strip().lower()
    if storage_provider not in {"cloudinary", "b2", "hybrid"}:
        raise RuntimeError("Kaggle worker requires durable STORAGE_PROVIDER=cloudinary, b2, or hybrid.")
    env["STORAGE_PROVIDER"] = storage_provider
    env["PYTHONPATH"] = str(backend)
    for name in (
        "REDIS_URL", "STORAGE_REPLICA_ENABLED", "STORAGE_REPLICA_PROVIDER", "B2_APPLICATION_KEY_ID", "B2_APPLICATION_KEY",
        "B2_BUCKET_NAME", "B2_REGION", "B2_ENDPOINT_URL", "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_STORAGE_BUCKET", "CLOUDINARY_CLOUD_NAME",
        "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET", "CLOUDFLARE_WHISPER_WORKER_URL",
        "CLOUDFLARE_WHISPER_SHARED_SECRET", "OAUTH_ENCRYPTION_KEY", "SESSION_SECRET",
        "SMTP_HOST", "SMTP_USERNAME", "SMTP_FROM_EMAIL", "FFMPEG_BINARY", "FFPROBE_BINARY",
        "WHISPER_COMMAND", "WHISPER_MODEL",
    ):
        value = secret(name, required=False)
        if value:
            env[name] = value
    required_storage_secrets = {
        "cloudinary": ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET"),
        "b2": ("B2_APPLICATION_KEY_ID", "B2_APPLICATION_KEY", "B2_BUCKET_NAME", "B2_REGION"),
        "hybrid": (
            "CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET",
            "B2_APPLICATION_KEY_ID", "B2_APPLICATION_KEY", "B2_BUCKET_NAME", "B2_REGION",
            "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_STORAGE_BUCKET",
        ),
    }
    missing = [name for name in required_storage_secrets[storage_provider] if not env.get(name)]
    if missing:
        raise RuntimeError(
            "Missing Kaggle Secrets for selected durable storage provider: " + ", ".join(missing)
        )
    if env.get("STORAGE_REPLICA_ENABLED", "").strip().lower() in {"1", "true", "yes"}:
        replica_provider = env.get("STORAGE_REPLICA_PROVIDER", "").strip().lower()
        if replica_provider not in {"cloudinary", "b2"} or replica_provider == storage_provider:
            raise RuntimeError("Invalid STORAGE_REPLICA_PROVIDER for Kaggle worker.")
        replica_missing = [name for name in required_storage_secrets[replica_provider] if not env.get(name)]
        if replica_missing:
            raise RuntimeError(
                "Missing Kaggle Secrets for storage replica: " + ", ".join(replica_missing)
            )
    worker_requirements = backend / "requirements-real-processing.txt"
    subprocess.run([
        "python", "-m", "pip", "install", "--disable-pip-version-check",
        "--no-cache-dir", "-r", str(worker_requirements),
    ], check=True, env=env)
    subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["ffprobe", "-version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Narrativ Forge Kaggle worker pinned to {TARGET_GIT_SHA}")
    subprocess.run(["python", "-m", "app.workers.kaggle_job_runner"], check=True, cwd=backend, env=env)

if __name__ == "__main__":
    main()