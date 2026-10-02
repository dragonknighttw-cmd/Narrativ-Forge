import os
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path

database_url = os.environ.get("DATABASE_URL", "")
backup = os.environ.get("BACKUP_FILE")
if not backup:
    raise SystemExit("BACKUP_FILE is required")

source = Path(backup)
if not source.is_file():
    raise SystemExit(f"Backup file not found: {source}")

if database_url.startswith("sqlite:///"):
    target = Path(database_url.removeprefix("sqlite:///"))
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as tmp:
        temp = Path(tmp.name)
    try:
        shutil.copy2(source, temp)
        with sqlite3.connect(temp) as db:
            result = db.execute("PRAGMA integrity_check").fetchone()
            if result != ("ok",):
                raise SystemExit("SQLite integrity check failed")
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)
elif database_url.startswith(("postgresql://", "postgres://")):
    subprocess.run(["pg_restore", "--clean", "--if-exists", "--no-owner", "--dbname", database_url, str(source)], check=True)
else:
    raise SystemExit("Unsupported DATABASE_URL; expected sqlite:/// or postgresql://")
print("restore complete")
