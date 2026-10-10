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


@pytest.mark.unit
def test_postgres_restore_requires_explicit_destructive_acknowledgement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "backup.dump"
    source.write_bytes(b"not used by this guard test")
    monkeypatch.delenv("ALLOW_DESTRUCTIVE_POSTGRES_RESTORE", raising=False)
    called = False

    def unexpected_run(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("pg_restore must not run without explicit acknowledgement")

    monkeypatch.setattr(restore_db.subprocess, "run", unexpected_run)

    with pytest.raises(SystemExit, match="Refusing destructive PostgreSQL restore"):
        restore_db.restore_postgres(source, "postgresql://user:pass@localhost/production")

    assert called is False


@pytest.mark.unit
def test_postgres_restore_runs_only_after_explicit_acknowledgement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "backup.dump"
    source.write_bytes(b"test")
    calls = []
    monkeypatch.setenv("ALLOW_DESTRUCTIVE_POSTGRES_RESTORE", "1")
    monkeypatch.setattr(restore_db.subprocess, "run", lambda args, **kwargs: calls.append((args, kwargs)))

    restore_db.restore_postgres(source, "postgresql://user:pass@localhost/restore_target")

    assert len(calls) == 1
    assert calls[0][1] == {"check": True}
    assert calls[0][0][:5] == [
        "pg_restore", "--clean", "--if-exists", "--no-owner", "--dbname"
    ]
