"""Bootstrap a one-job Narrativ Forge worker inside a Kaggle kernel."""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

from kaggle_secrets import UserSecretsClient

REPO = "dragonknighttw-cmd/Narrativ-Forge"
ROOT = Path("/kaggle/working/Narrativ-Forge")

def secret(name: str, *, required: bool = True) -> str:
    value = UserSecretsClient().get_secret(name)
    if required and not value:
        raise RuntimeError(f"Missing Kaggle Secret: {name}")
    return value or ""

def main() -> None:
    token = secret("GITHUB_TOKEN")
    database_url = secret("DATABASE_URL")
    if ROOT.exists():
        subprocess.run(["rm", "-rf", str(ROOT)], check=True)
    askpass = Path("/kaggle/working/git-askpass.sh")
    askpass.write_text("#!/bin/sh\ncase \"$1\" in\n*Username*) echo x-access-token ;;\n*) echo \"$GIT_PASSWORD\" ;;\nesac\n", encoding="utf-8")
    askpass.chmod(askpass.stat().st_mode | stat.S_IXUSR)
    clone_env = os.environ.copy()
    clone_env["GIT_ASKPASS"] = str(askpass)
    clone_env["GIT_PASSWORD"] = token
    clone_env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        subprocess.run(["git", "clone", "--depth", "1", f"https://github.com/{REPO}.git", str(ROOT)], check=True, stdout=subprocess.DEVNULL, env=clone_env)
    finally:
        askpass.unlink(missing_ok=True)
    backend = ROOT / "web-platform" / "backend"
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    env.setdefault("APP_ENV", "production")
    env["PYTHONPATH"] = str(backend)
    for name in (
        "REDIS_URL", "STORAGE_PROVIDER", "B2_APPLICATION_KEY_ID", "B2_APPLICATION_KEY",
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
    subprocess.run(["python", "-m", "pip", "install", "-r", str(backend / "requirements.txt")], check=True, env=env)
    subprocess.run(["python", "-m", "app.workers.kaggle_job_runner"], check=True, cwd=backend, env=env)

if __name__ == "__main__":
    main()