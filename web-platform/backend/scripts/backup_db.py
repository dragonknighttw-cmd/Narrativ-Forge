import os
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

database_url = os.environ.get("DATABASE_URL", "")
backup_dir = Path(os.environ.get("BACKUP_DIR", "./backups"))
backup_dir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

if database_url.startswith("sqlite:///"):
    source = Path(database_url.removeprefix("sqlite:///"))
    if not source.exists():
        raise SystemExit(f"SQLite database not found: {source}")
    target = backup_dir / f"narrativ-{stamp}.sqlite3"
    with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
        src.backup(dst)
    print(target)
elif database_url.startswith(("postgresql://", "postgres://")):
    target = backup_dir / f"narrativ-{stamp}.dump"
    subprocess.run(["pg_dump", "--format=custom", "--file", str(target), database_url], check=True)
    print(target)
else:
    raise SystemExit("Unsupported DATABASE_URL; expected sqlite:/// or postgresql://")
