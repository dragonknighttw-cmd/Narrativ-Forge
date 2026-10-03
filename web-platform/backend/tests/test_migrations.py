import os
from pathlib import Path
import subprocess
import sys

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect

from app import db


pytestmark = pytest.mark.integration

BACKEND_ROOT = Path(__file__).resolve().parents[1]
HEAD_REVISION = "0003_scene_script_scope"
PREVIOUS_REVISION = "0002_asset_storage_metadata"


def run_alembic(database_path: Path, *args: str) -> str:
    env = os.environ.copy()
    env["APP_ENV"] = "production"
    env["DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout + result.stderr


def migrated_schema(database_path: Path) -> dict[str, dict[str, object]]:
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        inspector = inspect(engine)
        return {
            table: {
                "columns": {column["name"] for column in inspector.get_columns(table)},
                "unique_constraints": {
                    (constraint["name"], tuple(constraint["column_names"]))
                    for constraint in inspector.get_unique_constraints(table)
                },
            }
            for table in inspector.get_table_names()
            if table != "alembic_version"
        }
    finally:
        engine.dispose()


def restore_legacy_scene_constraint(database_path: Path) -> None:
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        with engine.begin() as connection:
            operations = Operations(MigrationContext.configure(connection))
            with operations.batch_alter_table("scenes") as batch:
                batch.drop_constraint("uq_scene_number_per_script", type_="unique")
                batch.create_unique_constraint(
                    "uq_scene_number_per_episode",
                    ["episode_id", "scene_number"],
                )
    finally:
        engine.dispose()


def test_fresh_database_migrates_to_head_with_expected_schema(tmp_path):
    database_path = tmp_path / "fresh.db"

    output = run_alembic(database_path, "upgrade", "head")
    assert HEAD_REVISION in output

    schema = migrated_schema(database_path)
    assert {"users", "series", "episodes", "scripts", "scenes", "assets"} <= schema.keys()
    assert {"password_hash", "is_active", "updated_at"} <= schema["users"]["columns"]
    assert {"object_key", "checksum_sha256"} <= schema["assets"]["columns"]
    assert ("uq_scene_number_per_script", ("script_id", "scene_number")) in schema["scenes"]["unique_constraints"]
    assert ("uq_scene_number_per_episode", ("episode_id", "scene_number")) not in schema["scenes"]["unique_constraints"]


def test_upgrade_from_previous_revision_matches_fresh_schema(tmp_path):
    fresh_database = tmp_path / "fresh.db"
    upgraded_database = tmp_path / "from_previous.db"

    run_alembic(fresh_database, "upgrade", "head")
    run_alembic(upgraded_database, "upgrade", PREVIOUS_REVISION)
    restore_legacy_scene_constraint(upgraded_database)
    output = run_alembic(upgraded_database, "upgrade", "head")

    assert HEAD_REVISION in output
    assert migrated_schema(upgraded_database) == migrated_schema(fresh_database)

    run_alembic(upgraded_database, "downgrade", PREVIOUS_REVISION)
    downgraded_schema = migrated_schema(upgraded_database)
    assert ("uq_scene_number_per_episode", ("episode_id", "scene_number")) in downgraded_schema["scenes"]["unique_constraints"]
    assert ("uq_scene_number_per_script", ("script_id", "scene_number")) not in downgraded_schema["scenes"]["unique_constraints"]

    run_alembic(upgraded_database, "upgrade", "head")
    assert migrated_schema(upgraded_database) == migrated_schema(fresh_database)


@pytest.mark.parametrize("app_env", ["production", "staging"])
def test_non_development_startup_does_not_create_schema(monkeypatch, app_env):
    calls = []
    monkeypatch.setattr(db.settings, "app_env", app_env)
    monkeypatch.setattr(db.Base.metadata, "create_all", lambda **kwargs: calls.append(kwargs))

    db.init_db()

    assert calls == []
