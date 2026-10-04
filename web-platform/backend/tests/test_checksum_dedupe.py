import hashlib

import pytest

from test_foundation import auth_client


@pytest.mark.integration
def test_direct_checksum_dedupe_reuses_asset_and_storage_object(tmp_path):
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Checksum series"}).json()
        episode = client.post(
            "/api/v1/episodes",
            json={"series_id": series["id"], "episode_number": 1, "title": "Checksum episode"},
        ).json()
        body = b"checksum-dedupe-fixture"
        checksum = hashlib.sha256(body).hexdigest()

        first = client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("first.mp4", body, "video/mp4")},
            data={"asset_type": "video"},
            headers={"X-Content-SHA256": checksum},
        )
        assert first.status_code == 201

        second = client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("second.mp4", body, "video/mp4")},
            data={"asset_type": "video"},
            headers={"X-Content-SHA256": checksum},
        )
        assert second.status_code == 201
        assert second.json()["id"] == first.json()["id"]

        assets = client.get(f"/api/v1/episodes/{episode['id']}/assets")
        assert assets.status_code == 200
        assert len(assets.json()) == 1
    finally:
        client.close()


@pytest.mark.integration
def test_checksum_dedupe_reuses_object_for_another_episode(tmp_path):
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Cross episode checksum series"}).json()
        first_episode = client.post(
            "/api/v1/episodes",
            json={"series_id": series["id"], "episode_number": 1, "title": "Episode one"},
        ).json()
        second_episode = client.post(
            "/api/v1/episodes",
            json={"series_id": series["id"], "episode_number": 2, "title": "Episode two"},
        ).json()
        body = b"shared-storage-fixture"
        checksum = hashlib.sha256(body).hexdigest()

        first = client.post(
            f"/api/v1/episodes/{first_episode['id']}/assets/upload",
            files={"file": ("source.mp4", body, "video/mp4")},
            data={"asset_type": "video"},
            headers={"X-Content-SHA256": checksum},
        )
        second = client.post(
            f"/api/v1/episodes/{second_episode['id']}/assets/upload",
            files={"file": ("source.mp4", body, "video/mp4")},
            data={"asset_type": "video"},
            headers={"X-Content-SHA256": checksum},
        )
        assert first.status_code == second.status_code == 201
        assert second.json()["id"] != first.json()["id"]
        assert second.json()["object_key"] == first.json()["object_key"]
        assert second.json()["checksum_sha256"] == checksum
    finally:
        client.close()


@pytest.mark.integration
def test_checksum_header_mismatch_is_rejected():
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Checksum validation series"}).json()
        episode = client.post(
            "/api/v1/episodes",
            json={"series_id": series["id"], "episode_number": 1, "title": "Checksum validation episode"},
        ).json()
        response = client.post(
            f"/api/v1/episodes/{episode['id']}/assets/upload",
            files={"file": ("source.mp4", b"actual-content", "video/mp4")},
            data={"asset_type": "video"},
            headers={"X-Content-SHA256": "0" * 64},
        )
        assert response.status_code == 422
    finally:
        client.close()


@pytest.mark.integration
def test_resumable_checksum_dedupe_reuses_existing_asset():
    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Resumable checksum series"}).json()
        episode = client.post(
            "/api/v1/episodes",
            json={"series_id": series["id"], "episode_number": 1, "title": "Resumable checksum episode"},
        ).json()
        payload = {
            "episode_id": episode["id"],
            "original_filename": "source.mp4",
            "mime_type": "video/mp4",
            "asset_type": "video",
            "expected_size": 7,
        }

        first_session = client.post("/api/v1/uploads", json=payload).json()
        first_part = client.put(
            f"/api/v1/uploads/{first_session['id']}/chunks",
            params={"part_number": 1, "offset": 0},
            content=b"same123",
            headers={"Content-Type": "application/octet-stream"},
        )
        assert first_part.status_code == 200
        first_asset = client.post(f"/api/v1/uploads/{first_session['id']}/commit")
        assert first_asset.status_code == 201

        second_session = client.post("/api/v1/uploads", json=payload).json()
        second_part = client.put(
            f"/api/v1/uploads/{second_session['id']}/chunks",
            params={"part_number": 1, "offset": 0},
            content=b"same123",
            headers={"Content-Type": "application/octet-stream"},
        )
        assert second_part.status_code == 200
        second_asset = client.post(f"/api/v1/uploads/{second_session['id']}/commit")
        assert second_asset.status_code == 201
        assert second_asset.json()["id"] == first_asset.json()["id"]

        assets = client.get(f"/api/v1/episodes/{episode['id']}/assets")
        assert assets.status_code == 200
        assert len(assets.json()) == 1
    finally:
        client.close()
