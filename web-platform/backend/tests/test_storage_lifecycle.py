import pytest

pytestmark = pytest.mark.unit

from pathlib import Path

import pytest

from app.services.storage import LocalStorageProvider, StorageError


@pytest.mark.unit
def test_local_storage_upload_download_delete_and_checksum(tmp_path):
    provider = LocalStorageProvider(str(tmp_path))
    source = tmp_path / "source.bin"
    destination = tmp_path / "out" / "copy.bin"
    source.write_bytes(b"narrativ-forge-storage-fixture")

    stored = provider.upload_file(source, "episode-1/source.bin", "application/octet-stream")
    assert stored.provider == "local"
    assert stored.object_key == "episode-1/source.bin"
    assert stored.size_bytes == source.stat().st_size
    assert provider.exists(stored.object_key)

    downloaded = provider.download_file(stored.object_key, destination)
    assert destination.read_bytes() == source.read_bytes()
    assert downloaded.checksum_sha256 == stored.checksum_sha256

    provider.delete(stored.object_key)
    assert not provider.exists(stored.object_key)


@pytest.mark.unit
def test_local_storage_rejects_path_traversal(tmp_path):
    provider = LocalStorageProvider(str(tmp_path))
    source = tmp_path / "source.bin"
    source.write_bytes(b"fixture")
    for key in ("../escape.bin", "/absolute.bin", "episode/../escape.bin", "episode\\escape.bin"):
        with pytest.raises(StorageError):
            provider.upload_file(source, key, "application/octet-stream")


@pytest.mark.unit
def test_local_multipart_round_trip_is_resumable(tmp_path):
    provider = LocalStorageProvider(str(tmp_path))
    token = "resume-token"
    upload_id = provider.initiate_multipart_upload("episode-1/resume.bin", "application/octet-stream", token)
    provider.upload_part(upload_id, "episode-1/resume.bin", 1, b"hello ", False)
    provider.upload_part(upload_id, "episode-1/resume.bin", 2, b"world", True)

    parts = provider.list_multipart_parts(upload_id, "episode-1/resume.bin", token)
    assert [part["PartNumber"] for part in parts] == [1, 2]

    stored = provider.complete_multipart_upload(
        upload_id,
        "episode-1/resume.bin",
        parts,
        expected_size=11,
        chunk_size=6,
        upload_token=token,
    )
    assert provider.exists(stored.object_key)
    output = tmp_path / "multipart-out.bin"
    provider.download_file(stored.object_key, output)
    assert output.read_bytes() == b"hello world"



from app.services.storage_lifecycle import (
    StorageThresholds,
    can_delete_asset,
    classify_storage_usage,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("used", "capacity", "expected"),
    [
        (0, 100, "normal"),
        (79, 100, "normal"),
        (80, 100, "warning"),
        (89, 100, "warning"),
        (90, 100, "critical"),
        (94, 100, "critical"),
        (95, 100, "emergency"),
        (100, 100, "emergency"),
        (101, 100, "emergency"),
        (0, 0, "emergency"),
    ],
)
def test_storage_usage_state_boundaries(used, capacity, expected):
    usage = classify_storage_usage(used, capacity)
    assert usage.state() == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    ("used", "capacity"),
    [(-1, 100), (1, -1)],
)
def test_storage_usage_rejects_negative_sizes(used, capacity):
    with pytest.raises(ValueError, match="non-negative"):
        classify_storage_usage(used, capacity)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"is_final": False, "is_approved": False, "is_only_copy": False, "retention_expired": True}, True),
        ({"is_final": True, "is_approved": False, "is_only_copy": False, "retention_expired": True}, False),
        ({"is_final": False, "is_approved": True, "is_only_copy": False, "retention_expired": True}, False),
        ({"is_final": False, "is_approved": False, "is_only_copy": True, "retention_expired": True}, False),
        ({"is_final": False, "is_approved": False, "is_only_copy": False, "retention_expired": False}, False),
    ],
)
def test_asset_deletion_policy_preserves_approved_final_and_only_copies(kwargs, expected):
    assert can_delete_asset(**kwargs) is expected


@pytest.mark.unit
def test_storage_thresholds_must_be_ordered_and_in_range():
    with pytest.raises(ValueError, match="ordered"):
        StorageThresholds(warning=0.9, critical=0.8, emergency=0.95)
    with pytest.raises(ValueError, match="between 0 and 1"):
        StorageThresholds(warning=-0.1, critical=0.8, emergency=0.95)
