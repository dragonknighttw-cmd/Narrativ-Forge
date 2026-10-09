#!/usr/bin/env python3
"""Restore a SQLite or PostgreSQL backup.

SQLite restores are staged beside the target and only replace it after an explicit
PRAGMA integrity_check result of "ok". PostgreSQL restore is destructive and must
only target an intentionally selected restore database.
"""
from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def restore_sqlite(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp = destination.with_suffix(destination.suffix + ".restore")
    try:
        shutil.copy2(source, tmp)
        with sqlite3.connect(tmp) as check:
            result = check.execute("PRAGMA integrity_check").fetchone()
        if result != ("ok",):
            detail = result[0] if result else "no result"
            raise SystemExit(f"SQLite integrity check failed: {detail}")
        tmp.replace(destination)
    finally:
        tmp.unlink(missing_ok=True)


def restore_postgres(source: Path, database_url: str) -> None:
    subprocess.run(
        ["pg_restore", "--clean", "--if-exists", "--no-owner", "--dbname", database_url, str(source)],
        check=True,
    )


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    database_url = os.environ.get("DATABASE_URL", "sqlite:///./narrativ_forge.db")
    source = Path(args[0]) if args else None
    if source is None or not source.is_file():
        print("Usage: restore_db.py <backup-file>", file=sys.stderr)
        return 2

    if database_url.startswith("sqlite:///"):
        destination = Path(database_url.removeprefix("sqlite:///"))
        restore_sqlite(source, destination)
    elif database_url.startswith(("postgresql://", "postgres://")):
        restore_postgres(source, database_url)
    else:
        print("Unsupported DATABASE_URL scheme", file=sys.stderr)
        return 2

    print("restore complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
