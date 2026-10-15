from datetime import datetime, timedelta, timezone

import pytest

from app.core.config import settings
from app.models.core import Asset, AuditEvent, Episode, Series
from app.services.asset_gc import purge_deleted_assets
from app.services.storage import LocalStorageProvider, StorageError
from test_foundation import auth_client


@pytest.mark.unit
def test_gc_purges_old_deleted_assets(tmp_path, db_session, monkeypatch):
    monkeypatch.setattr(settings, "asset_retention_days", 30)
    series = Series(title="GC test series")
    db_session.add(series)
    db_session.flush()
    episode = Episode(series_id=series.id, public_id="gc-test-episode", episode_number=1, title="GC test episode")
    db_session.add(episode)
    db_session.flush()
    asset = Asset(
        episode_id=episode.id,
        storage_provider="local",
        local_path=str(tmp_path / "asset.bin"),
        object_key="asset.bin",
        original_filename="asset.bin",
        mime_type="application/octet-stream",
        file_size_bytes=1,
        version=1,
        asset_type="video",
        status="deleted",
    )
    asset.deleted_at = datetime.now(timezone.utc) - timedelta(days=31)
    db_session.add(asset)
    db_session.commit()
    (tmp_path / "asset.bin").write_bytes(b"x")
    monkeypatch.setattr("app.services.asset_gc.get_storage", lambda _: LocalStorageProvider(tmp_path))
    assert purge_deleted_assets(db_session) == 1
    assert db_session.get(Asset, asset.id) is None


@pytest.mark.integration
def test_recent_deleted_asset_is_retained():
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "GC series"}).json()
        episode = client.post("/api/v1/episodes", json={"series_id": series["id"], "episode_number": 1, "title": "GC episode"}).json()
        body = b"gc-fixture"
        response = client.post(f"/api/v1/episodes/{episode['id']}/assets/upload", files={"file": ("gc.mp4", body, "video/mp4")}, data={"asset_type": "video"})
        assert response.status_code == 201
        asset_id = response.json()["id"]
        deleted = client.delete(f"/api/v1/assets/{asset_id}")
        assert deleted.status_code == 200
    finally:
        client.close()


@pytest.mark.unit
def test_gc_preserves_asset_metadata_when_provider_delete_fails(tmp_path, db_session, monkeypatch):
    monkeypatch.setattr(settings, "asset_retention_days", 30)
    series = Series(title="GC provider failure series")
    db_session.add(series)
    db_session.flush()
    episode = Episode(
        series_id=series.id,
        public_id="gc-provider-failure-episode",
        episode_number=1,
        title="GC provider failure episode",
    )
    db_session.add(episode)
    db_session.flush()
    asset = Asset(
        episode_id=episode.id,
        storage_provider="local",
        local_path=str(tmp_path / "missing.bin"),
        object_key="missing.bin",
        original_filename="missing.bin",
        mime_type="application/octet-stream",
        file_size_bytes=1,
        version=1,
        asset_type="video",
        status="deleted",
    )
    asset.deleted_at = datetime.now(timezone.utc) - timedelta(days=31)
    db_session.add(asset)
    db_session.commit()
    asset_id = asset.id

    class FailingStorage:
        def delete(self, object_key):
            raise StorageError("simulated provider failure")

    monkeypatch.setattr("app.services.asset_gc.get_storage", lambda _: FailingStorage())

    assert purge_deleted_assets(db_session) == 0
    assert db_session.get(Asset, asset_id) is not None
    assert db_session.query(AuditEvent).filter_by(action="asset.purged", resource_id=asset_id).count() == 0
