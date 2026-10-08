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
