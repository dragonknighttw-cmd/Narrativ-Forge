#!/usr/bin/env python3
"""
Narrativ-Forge: Zero-Downtime Production Database Migration Runner
-----------------------------------------------------------------
Automates pre-deployment database migration verification, retries with backoff,
and runs `alembic upgrade head` safely before application servers start.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "apps/web-platform" / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from alembic import command
from alembic.config import Config


def verify_database_connection(db_url: str, max_retries: int = 5, retry_delay: int = 3) -> None:
    print(f"[*] Verifying database connectivity to {db_url.split('@')[-1]}...")
    
    # Strip special parameters that psycopg2/sqlalchemy might reject
    engine = create_engine(db_url, pool_pre_ping=True)
    
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("[+] Database connection verified successfully.")
            return
        except Exception as exc:
            if attempt >= max_retries:
                print(f"[!] Database connection failed after {max_retries} attempts: {exc}", file=sys.stderr)
                raise
            print(f"[-] Connection attempt {attempt}/{max_retries} failed ({exc}). Retrying in {retry_delay}s...")
            time.sleep(retry_delay)


def run_migrations(alembic_ini_path: Path) -> None:
    print(f"[*] Running database migrations with config: {alembic_ini_path}...")
    if not alembic_ini_path.exists():
        raise FileNotFoundError(f"Alembic configuration file not found at: {alembic_ini_path}")

    alembic_cfg = Config(str(alembic_ini_path))
    # Ensure script_location points to backend/alembic
    script_location = alembic_ini_path.parent / "alembic"
    alembic_cfg.set_main_option("script_location", str(script_location))

    try:
        command.upgrade(alembic_cfg, "head")
        print("[+] Migrations upgraded to 'head' successfully.")
    except Exception as exc:
        print(f"[!] Migration execution failed: {exc}", file=sys.stderr)
        raise


def main() -> int:
    print("=" * 65)
    print("  Narrativ-Forge: Production Database Migration Automation")
    print("=" * 65)

    db_url = os.getenv("DATABASE_URL", "").strip()
    if not db_url:
        print("[!] ERROR: DATABASE_URL environment variable is not set.", file=sys.stderr)
        return 1

    app_env = os.getenv("APP_ENV", "development").strip().lower()
    if app_env == "production" and db_url.startswith("sqlite"):
        print("[!] WARNING: Running SQLite in production is strongly discouraged. Use PostgreSQL.", file=sys.stderr)

    try:
        verify_database_connection(db_url)
        alembic_ini = backend_dir / "alembic.ini"
        run_migrations(alembic_ini)
        print("[+] Pre-deployment database verification and migration complete.")
        print("=" * 65)
        return 0
    except Exception as exc:
        print(f"[!] Fatal migration error: {exc}", file=sys.stderr)
        print("=" * 65)
        return 1


if __name__ == "__main__":
    sys.exit(main())
