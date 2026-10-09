from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
RESTORE_SCRIPT = REPO_ROOT / "scripts" / "restore_db.py"
SPEC = importlib.util.spec_from_file_location("narrativ_root_restore_db", RESTORE_SCRIPT)
assert SPEC is not None and SPEC.loader is not None
restore_db = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(restore_db)


@pytest.mark.unit
def test_sqlite_restore_replaces_target_only_after_integrity_check(tmp_path: Path) -> None:
    source = tmp_path / "backup.sqlite"
    target = tmp_path / "target.sqlite"

    with sqlite3.connect(source) as db:
        db.execute("CREATE TABLE evidence (value TEXT NOT NULL)")
        db.execute("INSERT INTO evidence(value) VALUES ('from-backup')")
    with sqlite3.connect(target) as db:
        db.execute("CREATE TABLE evidence (value TEXT NOT NULL)")
        db.execute("INSERT INTO evidence(value) VALUES ('old-target')")

    restore_db.restore_sqlite(source, target)

    with sqlite3.connect(target) as db:
        assert db.execute("SELECT value FROM evidence").fetchone() == ("from-backup",)
    assert not target.with_suffix(".sqlite.restore").exists()


@pytest.mark.unit
def test_sqlite_restore_does_not_replace_target_when_integrity_check_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "backup.sqlite"
    target = tmp_path / "target.sqlite"
    source.write_bytes(b"backup bytes")
    target.write_bytes(b"preserve existing target")

    class FailedIntegrityCheck:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def execute(self, _query: str):
            return self

        def fetchone(self):
            return ("database disk image is malformed",)

    monkeypatch.setattr(restore_db, "sqlite3", SimpleNamespace(connect=lambda _path: FailedIntegrityCheck()))

    with pytest.raises(SystemExit, match="SQLite integrity check failed"):
        restore_db.restore_sqlite(source, target)

    assert target.read_bytes() == b"preserve existing target"
    assert not target.with_suffix(".sqlite.restore").exists()
