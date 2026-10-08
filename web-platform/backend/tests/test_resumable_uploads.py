from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import hashlib
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import uploads
from app.core.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Asset, Episode, IdempotencyRecord, ProcessingJob, Scene, Series, UploadPart, UploadSession, User
from app.services.storage import (
    B2StorageProvider,
    LocalStorageProvider,
    MultipartUploadAlreadyCompleted,
    StorageError,
)
from app.services.passwords import hash_password
from app.api.dependencies import issue_session
from app.middleware.idempotency import request_fingerprint


@pytest.fixture
def upload_env(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestingSession() as db:
        owner = User(
            email=f"owner-{uuid4()}@test.local",
            role="owner",
            password_hash=hash_password("test-password-123"),
            is_active=True,
        )
        other = User(
            email=f"other-{uuid4()}@test.local",
            role="owner",
            password_hash=hash_password("test-password-123"),
            is_active=True,
        )
        viewer = User(
            email=f"viewer-{uuid4()}@test.local",
            role="viewer",
            password_hash=hash_password("test-password-123"),
            is_active=True,
        )
        series = Series(title=f"Uploads {uuid4()}")
        db.add_all([owner, other, viewer, series])
        db.flush()
        episode = Episode(
            public_id=f"UP-{uuid4()}",
            series_id=series.id,
            episode_number=1,
            title="Upload episode",
        )
        other_episode = Episode(
            public_id=f"UP-{uuid4()}",
            series_id=series.id,
            episode_number=2,
            title="Other episode",
        )
        db.add_all([episode, other_episode])
        db.flush()
        foreign_scene = Scene(
            episode_id=other_episode.id,
            scene_number=1,
            purpose="Foreign scene",
        )
        db.add(foreign_scene)
        db.commit()
        owner_id, other_id, viewer_id = owner.id, other.id, viewer.id
        episode_id, other_episode_id, foreign_scene_id = episode.id, other_episode.id, foreign_scene.id

    def override_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_db
    provider = LocalStorageProvider(str(tmp_path / "storage"))
    monkeypatch.setattr(uploads, "get_storage", lambda provider_name=None: provider)
    monkeypatch.setattr(settings, "storage_provider", "local")
    monkeypatch.setattr(settings, "upload_dir", str(tmp_path / "storage"))
    monkeypatch.setattr(settings, "max_upload_size_bytes", 50 * 1024 * 1024)
    monkeypatch.setattr(settings, "upload_chunk_size_bytes", 4)
    monkeypatch.setattr(settings, "upload_session_ttl_seconds", 86400)
    monkeypatch.setattr(settings, "session_secret", "test-session-secret-for-uploads")

    clients = []

    def client_for(email=None, role="owner"):
        host = f"127.0.0.{(uuid4().int % 253) + 1}"
        client = TestClient(app, base_url="http://localhost", client=(host, 12345))
        clients.append(client)
        if email:
            client.cookies.set("nf_session", issue_session(email, role))
        return client

    with TestingSession() as db:
        owner_email = db.get(User, owner_id).email
        other_email = db.get(User, other_id).email
        viewer_email = db.get(User, viewer_id).email
    yield {
        "db_factory": TestingSession,
        "provider": provider,
        "owner": client_for(owner_email),
        "other": client_for(other_email),
        "viewer": client_for(viewer_email, "viewer"),
        "episode_id": episode_id,
        "other_episode_id": other_episode_id,
        "foreign_scene_id": foreign_scene_id,
        "owner_id": owner_id,
        "other_id": other_id,
    }
    for client in clients:
        client.close()
    if previous_override is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = previous_override
    engine.dispose()


def create_session(env, size=10, **values):
    payload = {
        "episode_id": env["episode_id"],
        "original_filename": "source.mp4",
        "mime_type": "video/mp4",
        "asset_type": "video",
        "expected_size": size,
        **values,
    }
    return env["owner"].post("/api/v1/uploads", json=payload)


def put_part(client, session_id, part_number, offset, body, extra_headers=None):
    headers = {"Content-Type": "application/octet-stream", **(extra_headers or {})}
    return client.put(
        f"/api/v1/uploads/{session_id}/chunks",
        params={"part_number": part_number, "offset": offset},
        content=body,
        headers=headers,
    )


def test_create_auth_owner_and_episode_scene_validation(upload_env):
    env = upload_env
    payload = {
        "episode_id": env["episode_id"],
        "original_filename": "source.mp4",
        "mime_type": "video/mp4",
        "asset_type": "video",
        "expected_size": 10,
    }
    with TestClient(app, base_url="http://localhost", client=("127.0.0.254", 12345)) as unauthenticated:
        assert unauthenticated.post("/api/v1/uploads", json=payload).status_code == 401
    assert env["viewer"].post("/api/v1/uploads", json=payload).status_code == 403

    wrong_scene = env["owner"].post(
        "/api/v1/uploads",
        json={**payload, "scene_id": env["foreign_scene_id"]},
    )
    assert wrong_scene.status_code == 422

    created = env["owner"].post("/api/v1/uploads", json=payload)
    assert created.status_code == 201
    session = created.json()
    assert session["expected_size"] == 10
    assert session["chunk_size"] == 4
    assert session["expected_parts"] == 3
    assert "provider_upload_id" not in session

    with TestClient(app, base_url="http://localhost", client=("127.0.0.253", 12345)) as unauthenticated:
        assert unauthenticated.get(f"/api/v1/uploads/{session['id']}").status_code == 401
    assert env["other"].get(f"/api/v1/uploads/{session['id']}").status_code == 404
    assert put_part(env["other"], session["id"], 1, 0, b"abcd").status_code == 404
    wrong_episode = env["owner"].post(
        "/api/v1/uploads",
        json={**payload, "episode_id": "missing-episode"},
    )
    assert wrong_episode.status_code == 404


def test_chunks_are_offset_checked_resumable_and_commit_in_order(upload_env):
    env = upload_env
    session = create_session(env).json()
    session_id = session["id"]

    assert put_part(env["owner"], session_id, 1, 1, b"abcd").status_code == 422
    assert put_part(env["owner"], session_id, 1, 0, b"abc").status_code == 400
    assert put_part(env["owner"], session_id, 2, 4, b"efgh").status_code == 200
    resumed = env["owner"].get(f"/api/v1/uploads/{session_id}")
    assert resumed.status_code == 200
    assert [part["part_number"] for part in resumed.json()["parts"]] == [2]
    assert resumed.json()["parts"][0]["checksum_sha256"] == hashlib.sha256(b"efgh").hexdigest()

    assert env["owner"].post(f"/api/v1/uploads/{session_id}/commit").status_code == 409
    assert put_part(env["owner"], session_id, 1, 0, b"abcd").status_code == 200
    assert put_part(env["owner"], session_id, 1, 0, b"abcd").status_code == 200
    assert put_part(env["owner"], session_id, 3, 8, b"ij").status_code == 200

    committed = env["owner"].post(f"/api/v1/uploads/{session_id}/commit")
    assert committed.status_code == 200
    asset = committed.json()
    assert asset["episode_id"] == env["episode_id"]
    assert asset["version"] == 1
    assert asset["file_size_bytes"] == 10
    assert asset["original_filename"] == "source.mp4"
    assert asset["checksum_sha256"] == hashlib.sha256(b"abcdefghij").hexdigest()
    assert Path(asset["local_path"]).read_bytes() == b"abcdefghij"

    committed_again = env["owner"].post(f"/api/v1/uploads/{session_id}/commit")
    assert committed_again.status_code == 200
    assert committed_again.json()["id"] == asset["id"]
    resumed_committed = env["owner"].get(f"/api/v1/uploads/{session_id}")
    assert resumed_committed.json()["asset"]["id"] == asset["id"]


def test_duplicate_chunk_replaces_deterministically_and_commit_rejects_gap(upload_env):
    env = upload_env
    session = create_session(env, size=8).json()
    upload_id = session["id"]
    assert put_part(env["owner"], upload_id, 1, 0, b"aaaa").status_code == 200
    assert put_part(env["owner"], upload_id, 1, 0, b"bbbb").status_code == 200
    assert put_part(env["owner"], upload_id, 2, 4, b"cccc").status_code == 200
    result = env["owner"].post(f"/api/v1/uploads/{upload_id}/commit")
    assert result.status_code == 200
    assert Path(result.json()["local_path"]).read_bytes() == b"bbbbcccc"

    incomplete = create_session(env, size=8).json()
    assert put_part(env["owner"], incomplete["id"], 2, 4, b"cccc").status_code == 200
    response = env["owner"].post(f"/api/v1/uploads/{incomplete['id']}/commit")
    assert response.status_code == 409
    with env["db_factory"]() as db:
        assert db.query(Asset).filter(Asset.episode_id == env["episode_id"], Asset.version == 3).count() == 0
        assert db.get(UploadSession, incomplete["id"]).status == "active"


def test_existing_upload_route_respects_reserved_session_versions(upload_env):
    env = upload_env
    session = create_session(env, size=4).json()
    legacy_upload = env["owner"].post(
        f"/api/v1/episodes/{env['episode_id']}/assets/upload",
        files={"file": ("legacy.mp4", b"legacy", "video/mp4")},
        data={"asset_type": "video"},
    )
    assert legacy_upload.status_code == 201
    assert legacy_upload.json()["version"] == 2
    assert put_part(env["owner"], session["id"], 1, 0, b"data").status_code == 200
    committed = env["owner"].post(f"/api/v1/uploads/{session['id']}/commit")
    assert committed.status_code == 200
    assert committed.json()["version"] == 1


def test_chunk_count_boundary_and_expired_session_cleanup(upload_env, monkeypatch):
    env = upload_env
    monkeypatch.setattr(settings, "max_upload_size_bytes", 100_000)
    too_many = create_session(env, size=40_004)
    assert too_many.status_code == 413
    boundary = create_session(env, size=40_000)
    assert boundary.status_code == 201

    upload_id = boundary.json()["id"]
    with env["db_factory"]() as db:
        session = db.get(UploadSession, upload_id)
        session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    expired = env["owner"].get(f"/api/v1/uploads/{upload_id}")
    assert expired.status_code == 410
    with env["db_factory"]() as db:
        assert db.get(UploadSession, upload_id).status == "expired"
    with pytest.raises(StorageError):
        env["provider"].list_multipart_parts(
            db_session_upload_id(env, upload_id),
            db_session_object_key(env, upload_id),
        )


def db_session_upload_id(env, upload_id):
    with env["db_factory"]() as db:
        return db.get(UploadSession, upload_id).provider_upload_id


def db_session_object_key(env, upload_id):
    with env["db_factory"]() as db:
        return db.get(UploadSession, upload_id).object_key


def test_abort_is_owner_scoped_idempotent_and_prevents_later_writes(upload_env):
    env = upload_env
    session = create_session(env).json()
    upload_id = session["id"]
    assert env["other"].delete(f"/api/v1/uploads/{upload_id}").status_code == 404
    assert env["owner"].delete(f"/api/v1/uploads/{upload_id}").json()["status"] == "aborted"
    assert env["owner"].delete(f"/api/v1/uploads/{upload_id}").json()["status"] == "aborted"
    assert put_part(env["owner"], upload_id, 1, 0, b"abcd").status_code == 410


def test_failed_provider_commit_does_not_create_asset(upload_env, monkeypatch):
    env = upload_env
    session = create_session(env, size=4).json()
    assert put_part(env["owner"], session["id"], 1, 0, b"data").status_code == 200
    provider = env["provider"]
    original = provider.complete_multipart_upload

    def failed_completion(*args, **kwargs):
        raise StorageError("provider completion failed")

    monkeypatch.setattr(provider, "complete_multipart_upload", failed_completion)
    assert env["owner"].post(f"/api/v1/uploads/{session['id']}/commit").status_code == 502
    with env["db_factory"]() as db:
        assert db.query(Asset).filter(Asset.episode_id == env["episode_id"]).count() == 0
        assert db.get(UploadSession, session["id"]).status == "active"
    monkeypatch.setattr(provider, "complete_multipart_upload", original)
    assert env["owner"].post(f"/api/v1/uploads/{session['id']}/commit").status_code == 200


def test_completed_storage_upload_can_resume_database_finalization(upload_env):
    env = upload_env
    session = create_session(env, size=4).json()
    assert put_part(env["owner"], session["id"], 1, 0, b"data").status_code == 200
    with env["db_factory"]() as db:
        record = db.query(UploadPart).filter(
            UploadPart.upload_session_id == session["id"],
        ).one()
        upload = db.get(UploadSession, session["id"])
        parts = [{
            "PartNumber": record.part_number,
            "Size": record.size_bytes,
            "ETag": record.provider_etag,
        }]
        env["provider"].complete_multipart_upload(
            upload.provider_upload_id,
            upload.object_key,
            parts,
            upload.expected_size,
            upload.chunk_size,
            upload.id,
        )

    resumed = env["owner"].get(f"/api/v1/uploads/{session['id']}")
    assert resumed.status_code == 200
    assert len(resumed.json()["parts"]) == 1
    committed = env["owner"].post(f"/api/v1/uploads/{session['id']}/commit")
    assert committed.status_code == 200
    assert committed.json()["file_size_bytes"] == 4


def test_local_storage_binds_upload_to_key_validates_parts_and_reaps(upload_env):
    provider = LocalStorageProvider(upload_env["provider"].root.parent / "separate-local")
    key = "episodes/ep/assets/v1/video/source.mp4"
    token = str(uuid4())
    upload_id = provider.initiate_multipart_upload(key, "video/mp4", token)
    with pytest.raises(StorageError, match="object key mismatch"):
        provider.upload_part(upload_id, "episodes/other/source.mp4", 1, b"abcd", True)
    with pytest.raises(StorageError, match="Invalid multipart part number"):
        provider.upload_part(upload_id, key, 10001, b"abcd", True)

    etag1 = provider.upload_part(upload_id, key, 1, b"abcd", False)
    provider.upload_part(upload_id, key, 1, b"wxyz", False)
    etag2 = provider.upload_part(upload_id, key, 1, b"wxyz", False)
    with pytest.raises(StorageError, match="incomplete or inconsistent|changed"):
        provider.complete_multipart_upload(upload_id, key, [{"PartNumber": 1, "ETag": etag1, "Size": 4}], 4, 4, token)
    stored = provider.complete_multipart_upload(
        upload_id,
        key,
        [{"PartNumber": 1, "ETag": etag2, "Size": 4}],
        4,
        4,
        token,
    )
    assert stored.size_bytes == 4
    assert Path(stored.local_path).read_bytes() == b"wxyz"
    with pytest.raises(StorageError, match="cannot be aborted"):
        provider.abort_multipart_upload(upload_id, key)
    with pytest.raises(StorageError, match="object key mismatch"):
        provider.abort_multipart_upload(
            provider.initiate_multipart_upload(key, "video/mp4", str(uuid4())),
            "episodes/other/source.mp4",
        )


class FakeClientError(Exception):
    def __init__(self, code):
        self.response = {"Error": {"Code": code}}
        super().__init__(code)


class FakeB2Client:
    def __init__(self):
        self.uploads = {}
        self.objects = {}
        self.completed = 0
        self.aborted = []

    def create_multipart_upload(self, **kwargs):
        upload_id = str(uuid4())
        self.uploads[upload_id] = {
            "key": kwargs["Key"],
            "metadata": kwargs["Metadata"],
            "parts": {},
        }
        return {"UploadId": upload_id}

    def upload_part(self, **kwargs):
        upload = self.uploads[kwargs["UploadId"]]
        assert kwargs["Key"] == upload["key"]
        body = kwargs["Body"]
        etag = '"' + hashlib.md5(body, usedforsecurity=False).hexdigest() + '"'
        upload["parts"][kwargs["PartNumber"]] = {"Body": body, "ETag": etag}
        return {"ETag": etag}

    def list_parts(self, **kwargs):
        upload = self.uploads.get(kwargs["UploadId"])
        if not upload:
            raise FakeClientError("NoSuchUpload")
        assert kwargs["Key"] == upload["key"]
        parts = [
            {"PartNumber": number, "Size": len(item["Body"]), "ETag": item["ETag"]}
            for number, item in sorted(upload["parts"].items())
        ]
        return {"Parts": parts, "IsTruncated": False}

    def head_object(self, **kwargs):
        item = self.objects.get(kwargs["Key"])
        if not item:
            raise FakeClientError("404")
        return {"ContentLength": len(item["body"]), "Metadata": item["metadata"]}

    def get_object(self, **kwargs):
        return {"Body": BytesIO(self.objects[kwargs["Key"]]["body"])}

    def complete_multipart_upload(self, **kwargs):
        upload = self.uploads[kwargs["UploadId"]]
        body = b"".join(upload["parts"][part["PartNumber"]]["Body"] for part in kwargs["MultipartUpload"]["Parts"])
        self.objects[kwargs["Key"]] = {"body": body, "metadata": upload["metadata"]}
        self.uploads.pop(kwargs["UploadId"])
        self.completed += 1

    def abort_multipart_upload(self, **kwargs):
        self.aborted.append((kwargs["UploadId"], kwargs["Key"]))
        self.uploads.pop(kwargs["UploadId"], None)


def test_b2_multipart_uses_provider_parts_checks_etags_and_reconciles_retry():
    provider = B2StorageProvider.__new__(B2StorageProvider)
    provider.client = FakeB2Client()
    provider.bucket = "test-bucket"
    provider._client_error = FakeClientError
    key = "episodes/ep/assets/v1/video/source.mp4"
    token = str(uuid4())
    upload_id = provider.initiate_multipart_upload(key, "video/mp4", token)
    etag = provider.upload_part(upload_id, key, 1, b"small-final", True)
    with pytest.raises(StorageError, match="5 MiB"):
        provider.upload_part(upload_id, key, 2, b"small-nonfinal", False)

    bad_parts = [{"PartNumber": 1, "ETag": '"wrong"', "Size": 11}]
    with pytest.raises(StorageError, match="incomplete or inconsistent"):
        provider.complete_multipart_upload(upload_id, key, bad_parts, 11, 16, token)
    duplicate_parts = [{"PartNumber": 1, "ETag": etag, "Size": 11}] * 2
    with pytest.raises(StorageError, match="incomplete or inconsistent"):
        provider.complete_multipart_upload(upload_id, key, duplicate_parts, 11, 16, token)
    assert provider.client.completed == 0

    parts = [{"PartNumber": 1, "ETag": etag, "Size": 11}]
    stored = provider.complete_multipart_upload(upload_id, key, parts, 11, 16, token)
    assert stored.checksum_sha256 == hashlib.sha256(b"small-final").hexdigest()
    assert provider.client.completed == 1
    assert provider.complete_multipart_upload(upload_id, key, parts, 11, 16, token) == stored
    assert provider.client.completed == 1
    with pytest.raises(MultipartUploadAlreadyCompleted):
        provider.list_multipart_parts(upload_id, key, token, 11)
    provider.abort_multipart_upload(str(uuid4()), key)
    assert provider.client.aborted[-1][1] == key


def test_idempotent_upload_session_replay_mismatch_and_actor_scope(upload_env):
    env = upload_env
    key = str(uuid4())
    headers = {"Idempotency-Key": key}
    first = env["owner"].post(
        "/api/v1/uploads",
        json={
            "episode_id": env["episode_id"],
            "original_filename": "source.mp4",
            "mime_type": "video/mp4",
            "asset_type": "video",
            "expected_size": 10,
        },
        headers=headers,
    )
    replay = env["owner"].post(
        "/api/v1/uploads",
        json={
            "episode_id": env["episode_id"],
            "original_filename": "source.mp4",
            "mime_type": "video/mp4",
            "asset_type": "video",
            "expected_size": 10,
        },
        headers=headers,
    )
    assert first.status_code == replay.status_code == 201
    assert replay.json() == first.json()
    with env["db_factory"]() as db:
        assert db.query(UploadSession).filter(UploadSession.owner_id == env["owner_id"]).count() == 1
        stored = db.query(IdempotencyRecord).filter(IdempotencyRecord.key == key).one()
        assert stored.status == "completed"
        assert stored.response_status == 201
        assert first.json()["id"] in stored.response_body

    mismatch = env["owner"].post(
        "/api/v1/uploads",
        json={
            "episode_id": env["episode_id"],
            "original_filename": "source.mp4",
            "mime_type": "video/mp4",
            "asset_type": "video",
            "expected_size": 11,
        },
        headers=headers,
    )
    assert mismatch.status_code == 409

    other_user = env["other"].post(
        "/api/v1/uploads",
        json={
            "episode_id": env["episode_id"],
            "original_filename": "source.mp4",
            "mime_type": "video/mp4",
            "asset_type": "video",
            "expected_size": 10,
        },
        headers=headers,
    )
    assert other_user.status_code == 201
    assert other_user.json()["id"] != first.json()["id"]


def test_idempotent_direct_asset_hashes_content_and_prevents_duplicate_assets(upload_env):
    env = upload_env
    key = str(uuid4())
    endpoint = f"/api/v1/episodes/{env['episode_id']}/assets/upload"

    def upload(body):
        return env["owner"].post(
            endpoint,
            files={"file": ("source.mp4", body, "video/mp4")},
            data={"asset_type": "video"},
            headers={"Idempotency-Key": key},
        )

    first = upload(b"asset-fixture")
    replay = upload(b"asset-fixture")
    assert first.status_code == replay.status_code == 201
    assert replay.json() == first.json()
    assert upload(b"different-content").status_code == 409
    with env["db_factory"]() as db:
        assert db.query(Asset).filter(Asset.episode_id == env["episode_id"]).count() == 1
        stored = db.query(IdempotencyRecord).filter(IdempotencyRecord.key == key).one()
        assert b"asset-fixture" not in stored.response_body.encode("utf-8")


def test_idempotent_job_replay_and_same_key_different_endpoint_conflict(upload_env):
    env = upload_env
    key = str(uuid4())
    headers = {"Idempotency-Key": key}
    payload = {"episode_id": env["episode_id"]}
    first = env["owner"].post("/api/v1/jobs/real", json=payload, headers=headers)
    replay = env["owner"].post("/api/v1/jobs/real", json=payload, headers=headers)
    assert first.status_code == replay.status_code == 201
    assert first.json() == replay.json()
    assert env["owner"].post("/api/v1/jobs/mock", json=payload, headers=headers).status_code == 409
    with env["db_factory"]() as db:
        assert db.query(ProcessingJob).filter(ProcessingJob.episode_id == env["episode_id"]).count() == 1


def test_idempotent_mock_job_reuses_job_after_processing(upload_env):
    env = upload_env
    key = str(uuid4())
    payload = {"episode_id": env["episode_id"]}
    headers = {"Idempotency-Key": key}
    first = env["owner"].post("/api/v1/jobs/mock", json=payload, headers=headers)
    replay = env["owner"].post("/api/v1/jobs/mock", json=payload, headers=headers)
    assert first.status_code == replay.status_code == 201
    assert replay.json() == first.json()
    with env["db_factory"]() as db:
        assert db.query(ProcessingJob).filter(ProcessingJob.episode_id == env["episode_id"]).count() == 1


def test_incomplete_job_idempotency_record_recovers_existing_resource(upload_env):
    env = upload_env
    key = str(uuid4())
    path = "/api/v1/jobs/real"
    job_id = str(uuid4())
    payload = {"episode_id": env["episode_id"], "job_type": "real_processing"}
    with env["db_factory"]() as db:
        db.add(ProcessingJob(
            id=job_id,
            episode_id=env["episode_id"],
            job_type="real_processing",
            status="queued",
            progress=0,
        ))
        db.add(IdempotencyRecord(
            actor_id=env["owner_id"],
            key=key,
            method="POST",
            target=path,
            request_fingerprint=request_fingerprint("POST", path, payload),
            status="processing",
            resource_type="processing_job",
            resource_id=job_id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ))
        db.commit()

    response = env["owner"].post(
        path,
        json={"episode_id": env["episode_id"]},
        headers={"Idempotency-Key": key},
    )
    assert response.status_code == 201
    assert response.json()["id"] == job_id
    with env["db_factory"]() as db:
        record = db.query(IdempotencyRecord).filter(IdempotencyRecord.key == key).one()
        assert record.status == "completed"
        assert job_id in record.response_body


def test_idempotency_validation_failures_are_retryable_and_keys_are_bounded(upload_env):
    env = upload_env
    key = str(uuid4())
    invalid = env["owner"].post(
        "/api/v1/jobs/real",
        json={"episode_id": "missing-episode"},
        headers={"Idempotency-Key": key},
    )
    assert invalid.status_code == 404
    with env["db_factory"]() as db:
        assert db.query(IdempotencyRecord).filter(IdempotencyRecord.key == key).count() == 0

    retry = env["owner"].post(
        "/api/v1/jobs/real",
        json={"episode_id": env["episode_id"]},
        headers={"Idempotency-Key": key},
    )
    assert retry.status_code == 201
    assert env["owner"].post(
        "/api/v1/jobs/real",
        json={"episode_id": env["episode_id"]},
        headers={"Idempotency-Key": "x" * 256},
    ).status_code == 400
    assert env["owner"].post(
        "/api/v1/jobs/real",
        json={"episode_id": env["episode_id"]},
        headers={"Idempotency-Key": ""},
    ).status_code == 400


def test_expired_idempotency_key_is_reusable_and_unkeyed_requests_remain_optional(upload_env):
    env = upload_env
    key = str(uuid4())
    payload = {"episode_id": env["episode_id"]}
    first = env["owner"].post(
        "/api/v1/jobs/real",
        json=payload,
        headers={"Idempotency-Key": key},
    )
    with env["db_factory"]() as db:
        record = db.query(IdempotencyRecord).filter(IdempotencyRecord.key == key).one()
        record.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    reused = env["owner"].post(
        "/api/v1/jobs/real",
        json=payload,
        headers={"Idempotency-Key": key},
    )
    assert reused.status_code == 201
    assert reused.json()["id"] != first.json()["id"]

    unkeyed_first = env["owner"].post("/api/v1/jobs/real", json=payload)
    unkeyed_second = env["owner"].post("/api/v1/jobs/real", json=payload)
    assert unkeyed_first.status_code == unkeyed_second.status_code == 201
    assert unkeyed_first.json()["id"] != unkeyed_second.json()["id"]


def test_chunk_put_does_not_create_or_consume_idempotency_record(upload_env):
    env = upload_env
    session = create_session(env, size=4).json()
    response = put_part(
        env["owner"],
        session["id"],
        1,
        0,
        b"data",
        extra_headers={"Idempotency-Key": str(uuid4())},
    )
    assert response.status_code == 200
    with env["db_factory"]() as db:
        assert db.query(IdempotencyRecord).count() == 0
