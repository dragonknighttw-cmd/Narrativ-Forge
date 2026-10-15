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
HEAD_REVISION = "0018_tenant_backfill_guard"
PREVIOUS_REVISION = "0008_storage_replicas"


def run_alembic(database_path: Path, *args: str) -> str:
    env = os.environ.copy()
    env["APP_ENV"] = "production"
    env["DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise AssertionError(
            f"alembic {' '.join(args)} failed with {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
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
    assert {
        "users", "series", "episodes", "scripts", "scenes", "assets",
        "upload_sessions", "upload_parts", "idempotency_records",
    } <= schema.keys()
    assert {"password_hash", "is_active", "updated_at"} <= schema["users"]["columns"]
    assert "row_version" in schema["episodes"]["columns"]
    assert "row_version" in schema["scripts"]["columns"]
    assert {"object_key", "checksum_sha256"} <= schema["assets"]["columns"]
    assert {"max_retries", "next_run_at", "last_error"} <= schema["processing_jobs"]["columns"]
    assert {
        "id",
        "processing_job_id",
        "reason",
        "retry_count",
        "created_at",
        "resolved_at",
        "dlq_published_at",
    } <= schema["failed_jobs"]["columns"]
    assert {
        "id", "owner_id", "episode_id", "reserved_version", "asset_type", "scene_id",
        "original_filename", "mime_type", "expected_size", "chunk_size", "copyright_status",
        "storage_provider", "object_key", "provider_upload_id", "status", "created_at",
        "last_activity_at", "expires_at",
    } <= schema["upload_sessions"]["columns"]
    assert {
        "id", "upload_session_id", "part_number", "size_bytes", "checksum_sha256",
        "provider_etag", "created_at",
    } <= schema["upload_parts"]["columns"]
    assert {
        "id", "actor_id", "key", "method", "target", "request_fingerprint",
        "status", "resource_type", "resource_id", "response_status", "response_body",
        "response_content_type", "created_at", "updated_at", "expires_at",
    } <= schema["idempotency_records"]["columns"]
    assert ("uq_idempotency_actor_key", ("actor_id", "key")) in schema[
        "idempotency_records"
    ]["unique_constraints"]
    assert ("uq_scene_number_per_script", ("script_id", "scene_number")) in schema["scenes"]["unique_constraints"]
    assert ("uq_scene_number_per_episode", ("episode_id", "scene_number")) not in schema["scenes"]["unique_constraints"]
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        failed_indexes = {index["name"]: index for index in inspect(engine).get_indexes("failed_jobs")}
        assert failed_indexes["uq_failed_jobs_active_processing_job"]["unique"] == 1
        assert "ix_processing_jobs_dispatch_due" in {
            index["name"] for index in inspect(engine).get_indexes("processing_jobs")
        }
        assert "ix_idempotency_records_expires_at" in {
            index["name"] for index in inspect(engine).get_indexes("idempotency_records")
        }
    finally:
        engine.dispose()


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


def test_retry_dlq_migration_round_trip_from_current_baseline(tmp_path):
    database_path = tmp_path / "retry_dlq.db"
    run_alembic(database_path, "upgrade", "head")

    run_alembic(database_path, "downgrade", PREVIOUS_REVISION)
    schema = migrated_schema(database_path)
    assert "failed_jobs" in schema
    assert {"max_retries", "next_run_at", "last_error"} <= schema["processing_jobs"]["columns"]

    run_alembic(database_path, "upgrade", "head")
    schema = migrated_schema(database_path)
    assert "failed_jobs" in schema
    assert {"max_retries", "next_run_at", "last_error"} <= schema["processing_jobs"]["columns"]


def test_retry_dlq_migration_upgrades_an_existing_0003_schema(tmp_path):
    database_path = tmp_path / "existing_0003.db"
    run_alembic(database_path, "upgrade", "0003_scene_script_scope")

    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql("DROP INDEX IF EXISTS ix_processing_jobs_dispatch_due")
            connection.exec_driver_sql("DROP TABLE IF EXISTS failed_jobs")
            for column in ("last_error", "next_run_at", "max_retries"):
                connection.exec_driver_sql(f"ALTER TABLE processing_jobs DROP COLUMN {column}")
    finally:
        engine.dispose()

    output = run_alembic(database_path, "upgrade", "head")
    assert HEAD_REVISION in output
    schema = migrated_schema(database_path)
    assert {"max_retries", "next_run_at", "last_error"} <= schema["processing_jobs"]["columns"]
    assert "failed_jobs" in schema


def test_upload_migration_upgrades_an_existing_0004_schema(tmp_path):
    database_path = tmp_path / "existing_0004.db"
    run_alembic(database_path, "upgrade", "0004_processing_retry_dlq")

    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql("DROP TABLE IF EXISTS upload_parts")
            connection.exec_driver_sql("DROP TABLE IF EXISTS upload_sessions")
    finally:
        engine.dispose()

    output = run_alembic(database_path, "upgrade", "head")
    assert HEAD_REVISION in output
    schema = migrated_schema(database_path)
    assert {"upload_sessions", "upload_parts"} <= schema.keys()
    assert "expected_size" in schema["upload_sessions"]["columns"]


def test_idempotency_migration_upgrades_existing_0005_schema(tmp_path):
    database_path = tmp_path / "existing_0005.db"
    run_alembic(database_path, "upgrade", "0005_resumable_uploads")
    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql("DROP TABLE IF EXISTS idempotency_records")
    finally:
        engine.dispose()

    output = run_alembic(database_path, "upgrade", "head")
    assert HEAD_REVISION in output
    schema = migrated_schema(database_path)
    assert "idempotency_records" in schema
    assert ("uq_idempotency_actor_key", ("actor_id", "key")) in schema[
        "idempotency_records"
    ]["unique_constraints"]

    run_alembic(database_path, "downgrade", "0005_resumable_uploads")
    assert "idempotency_records" not in migrated_schema(database_path)


@pytest.mark.parametrize("app_env", ["production", "staging"])
def test_non_development_startup_does_not_create_schema(monkeypatch, app_env):
    calls = []
    monkeypatch.setattr(db.settings, "app_env", app_env)
    monkeypatch.setattr(db.Base.metadata, "create_all", lambda **kwargs: calls.append(kwargs))

    db.init_db()

    assert calls == []


def test_tenant_backfill_guard_never_assigns_ambiguous_memberships(tmp_path):
    database_path = tmp_path / "tenant_backfill_guard.db"
    run_alembic(database_path, "upgrade", "0013_tenant_scope_integrations")

    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        with engine.begin() as connection:
            for org_id, slug in (("org-a", "org-a"), ("org-b", "org-b"), ("org-c", "org-c")):
                connection.exec_driver_sql(
                    "INSERT INTO organizations (id, name, slug, plan, created_at, updated_at) "
                    "VALUES (?, ?, ?, 'trial', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                    (org_id, slug, slug),
                )
            for user_id, email in (
                ("user-ambiguous", "ambiguous@example.test"),
                ("user-single", "single@example.test"),
            ):
                connection.exec_driver_sql(
                    "INSERT INTO users (id, email, role, password_hash, is_active, created_at, updated_at) "
                    "VALUES (?, ?, 'owner', 'test-hash', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                    (user_id, email),
                )
            for membership_id, org_id, user_id in (
                ("m-a", "org-a", "user-ambiguous"),
                ("m-b", "org-b", "user-ambiguous"),
                ("m-c", "org-c", "user-single"),
            ):
                connection.exec_driver_sql(
                    "INSERT INTO organization_memberships (id, organization_id, user_id, role, created_at) "
                    "VALUES (?, ?, ?, 'owner', CURRENT_TIMESTAMP)",
                    (membership_id, org_id, user_id),
                )

            connection.exec_driver_sql(
                "INSERT INTO audit_events (id, actor_email, action, resource_type, resource_id, metadata_json, created_at, organization_id) "
                "VALUES ('audit-ambiguous', 'ambiguous@example.test', 'read', 'series', 'series-a', '{}', CURRENT_TIMESTAMP, 'org-a')"
            )
            connection.exec_driver_sql(
                "INSERT INTO audit_events (id, actor_email, action, resource_type, resource_id, metadata_json, created_at, organization_id) "
                "VALUES ('audit-single', 'single@example.test', 'read', 'series', 'series-c', '{}', CURRENT_TIMESTAMP, NULL)"
            )
            connection.exec_driver_sql(
                "INSERT INTO google_drive_connections (id, user_email, refresh_token_encrypted, organization_id, scope, created_at, updated_at) "
                "VALUES ('drive-ambiguous', 'ambiguous@example.test', 'encrypted-test', 'org-a', '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
            connection.exec_driver_sql(
                "INSERT INTO google_drive_connections (id, user_email, refresh_token_encrypted, organization_id, scope, created_at, updated_at) "
                "VALUES ('drive-single', 'single@example.test', 'encrypted-test', NULL, '', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )

    finally:
        engine.dispose()

    run_alembic(database_path, "upgrade", "0018_tenant_backfill_guard")

    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    try:
        with engine.connect() as connection:
            audit = dict(connection.exec_driver_sql(
                "SELECT id, organization_id FROM audit_events"
            ).all())
            drive = dict(connection.exec_driver_sql(
                "SELECT id, organization_id FROM google_drive_connections"
            ).all())
        assert audit["audit-ambiguous"] is None
        assert audit["audit-single"] == "org-c"
        assert drive["drive-ambiguous"] is None
        assert drive["drive-single"] == "org-c"
    finally:
        engine.dispose()
