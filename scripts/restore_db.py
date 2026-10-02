#!/usr/bin/env python3
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

database_url = os.environ.get("DATABASE_URL", "sqlite:///./narrativ_forge.db")
source = Path(sys.argv[1]) if len(sys.argv) > 1 else None
if not source or not source.exists():
    raise SystemExit("Usage: restore_db.py <backup-file>")

if database_url.startswith("sqlite:///"):
    destination = Path(database_url.removeprefix("sqlite:///"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_suffix(destination.suffix + ".restore")
    shutil.copy2(source, tmp)
    check = sqlite3.connect(tmp)
    try:
        check.execute("PRAGMA integrity_check")
        check.commit()
    finally:
        check.close()
    tmp.replace(destination)
elif database_url.startswith(("postgresql://", "postgres://")):
    result = subprocess.run(
        ["pg_restore", "--clean", "--if-exists", "--no-owner", "--dbname", database_url, str(source)],
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)
else:
    raise SystemExit("Unsupported DATABASE_URL scheme")

print("restore complete")
