#!/usr/bin/env python3
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

database_url = os.environ.get("DATABASE_URL", "sqlite:///./narrativ_forge.db")
backup_dir = Path(os.environ.get("BACKUP_DIR", "./backups"))
backup_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

if database_url.startswith("sqlite:///"):
    source = Path(database_url.removeprefix("sqlite:///"))
    destination = backup_dir / f"narrativ_forge-{stamp}.db"
    source_db = sqlite3.connect(source)
    target_db = sqlite3.connect(destination)
    try:
        source_db.backup(target_db)
    finally:
        target_db.close()
        source_db.close()
elif database_url.startswith(("postgresql://", "postgres://")):
    destination = backup_dir / f"narrativ_forge-{stamp}.dump"
    result = subprocess.run(["pg_dump", "--format=custom", "--file", str(destination), database_url], check=False)
    if result.returncode != 0:
        raise SystemExit(result.returncode)
else:
    raise SystemExit("Unsupported DATABASE_URL scheme")

print(destination)
