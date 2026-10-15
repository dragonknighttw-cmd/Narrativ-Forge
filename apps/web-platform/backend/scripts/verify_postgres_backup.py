#!/usr/bin/env python3
"""Non-destructive PostgreSQL backup verification."""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="pg_dump archive or directory")
    args = parser.parse_args()
    archive = args.archive
    if not archive.exists():
        print(f"backup not found: {archive}", file=sys.stderr)
        return 2
    pg_restore = shutil.which("pg_restore")
    if not pg_restore:
        print("pg_restore is required", file=sys.stderr)
        return 2
    result = subprocess.run([pg_restore, "--list", str(archive)], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip() or "pg_restore could not inspect the backup", file=sys.stderr)
        return result.returncode
    entries = [line for line in result.stdout.splitlines() if line and not line.startswith(";")]
    if not entries:
        print("backup archive contains no restorable entries", file=sys.stderr)
        return 1
    print(f"backup verification passed: {len(entries)} archive entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
