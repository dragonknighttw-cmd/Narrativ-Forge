import pytest


@pytest.mark.integration
def test_episode_optimistic_lock_requires_version_and_rejects_stale_writer():
    from test_foundation import auth_client

    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Optimistic episode series"}).json()
        episode = client.post(
            "/api/v1/episodes",
            json={"series_id": series["id"], "episode_number": 1, "title": "Optimistic episode"},
        ).json()
        assert episode["row_version"] == 1

        missing = client.patch(
            f"/api/v1/episodes/{episode['id']}",
            json={"title": "Missing version"},
        )
        assert missing.status_code == 422

        first = client.patch(
            f"/api/v1/episodes/{episode['id']}",
            json={"title": "Writer A", "expected_row_version": episode["row_version"]},
        )
        assert first.status_code == 200
        assert first.json()["row_version"] == 2

        stale = client.patch(
            f"/api/v1/episodes/{episode['id']}",
            json={"title": "Writer B", "expected_row_version": episode["row_version"]},
        )
        assert stale.status_code == 409
        detail = stale.json()["detail"]
        assert detail["code"] == "STALE_ROW_VERSION"
        assert detail["current"]["id"] == episode["id"]
        assert detail["current"]["row_version"] == 2
        assert detail["current"]["title"] == "Writer A"

        current = client.patch(
            f"/api/v1/episodes/{episode['id']}",
            json={"title": "Writer B", "expected_row_version": 2},
        )
        assert current.status_code == 200
        assert current.json()["row_version"] == 3
    finally:
        client.close()


@pytest.mark.integration
def test_script_optimistic_lock_requires_version_and_rejects_stale_writer():
    from test_foundation import auth_client

    client = auth_client()
    try:
        series = client.post("/api/v1/series", json={"title": "Optimistic script series"}).json()
        episode = client.post(
            "/api/v1/episodes",
            json={"series_id": series["id"], "episode_number": 1, "title": "Optimistic script episode"},
        ).json()
        script = client.post(
            f"/api/v1/episodes/{episode['id']}/scripts",
            json={"title": "Draft", "content": "Original"},
        ).json()
        assert script["row_version"] == 1

        missing = client.patch(
            f"/api/v1/scripts/{script['id']}",
            json={"content": "Missing version"},
        )
        assert missing.status_code == 422

        first = client.patch(
            f"/api/v1/scripts/{script['id']}",
            json={"content": "Writer A", "expected_row_version": script["row_version"]},
        )
        assert first.status_code == 200
        assert first.json()["row_version"] == 2

        stale = client.patch(
            f"/api/v1/scripts/{script['id']}",
            json={"content": "Writer B", "expected_row_version": script["row_version"]},
        )
        assert stale.status_code == 409
        detail = stale.json()["detail"]
        assert detail["code"] == "STALE_ROW_VERSION"
        assert detail["current"]["row_version"] == 2
        assert detail["current"]["content"] == "Writer A"

        current = client.patch(
            f"/api/v1/scripts/{script['id']}",
            json={"content": "Writer B", "expected_row_version": 2},
        )
        assert current.status_code == 200
        assert current.json()["row_version"] == 3
    finally:
        client.close()
