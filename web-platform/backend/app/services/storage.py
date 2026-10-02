from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..core.config import settings


class StorageError(RuntimeError):
    pass


@dataclass(frozen=True)
class StoredObject:
    provider: str
    object_key: str
    size_bytes: int
    checksum_sha256: str
    local_path: str | None = None


class StorageProvider(Protocol):
    name: str

    def upload_file(self, source: Path, object_key: str, content_type: str) -> StoredObject: ...
    def download_file(self, object_key: str, destination: Path) -> StoredObject: ...
    def delete(self, object_key: str) -> None: ...
    def exists(self, object_key: str) -> bool: ...
    def download_url(self, object_key: str) -> str | None: ...


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_object_key(object_key: str) -> str:
    normalized = object_key.replace("\\", "/").lstrip("/")
    parts = [part for part in normalized.split("/") if part not in {"", ".", ".."}]
    if not parts:
        raise StorageError("Invalid storage object key")
    return "/".join(parts)


class LocalStorageProvider:
    name = "local"

    def __init__(self, root: str | None = None):
        self.root = Path(root or settings.upload_dir) / "objects"
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, object_key: str) -> Path:
        key = _safe_object_key(object_key)
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def upload_file(self, source: Path, object_key: str, content_type: str) -> StoredObject:
        destination = self._path(object_key)
        shutil.copy2(source, destination)
        return StoredObject(
            provider=self.name,
            object_key=_safe_object_key(object_key),
            size_bytes=destination.stat().st_size,
            checksum_sha256=sha256_file(destination),
            local_path=str(destination),
        )

    def download_file(self, object_key: str, destination: Path) -> StoredObject:
        source = self._path(object_key)
        if not source.is_file():
            raise StorageError("Storage object not found")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return StoredObject(
            provider=self.name,
            object_key=_safe_object_key(object_key),
            size_bytes=destination.stat().st_size,
            checksum_sha256=sha256_file(destination),
            local_path=str(destination),
        )

    def delete(self, object_key: str) -> None:
        self._path(object_key).unlink(missing_ok=True)

    def exists(self, object_key: str) -> bool:
        return self._path(object_key).is_file()

    def download_url(self, object_key: str) -> str | None:
        return None


class B2StorageProvider:
    name = "b2"

    def __init__(self):
        if not all([
            settings.b2_application_key_id,
            settings.b2_application_key,
            settings.b2_bucket_name,
            settings.b2_region,
        ]):
            raise StorageError("B2 storage is not configured")
        try:
            import boto3
            from botocore.config import Config
        except ImportError as exc:
            raise StorageError("boto3 is required for B2 storage") from exc

        endpoint = settings.b2_endpoint_url or f"https://s3.{settings.b2_region}.backblazeb2.com"
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=settings.b2_application_key_id,
            aws_secret_access_key=settings.b2_application_key,
            region_name=settings.b2_region,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.b2_bucket_name

    def upload_file(self, source: Path, object_key: str, content_type: str) -> StoredObject:
        key = _safe_object_key(object_key)
        checksum = sha256_file(source)
        size = source.stat().st_size
        try:
            self.client.upload_file(
                str(source),
                self.bucket,
                key,
                ExtraArgs={
                    "ContentType": content_type,
                    "Metadata": {"sha256": checksum},
                },
            )
        except Exception as exc:
            raise StorageError("B2 upload failed") from exc
        return StoredObject(
            provider=self.name,
            object_key=key,
            size_bytes=size,
            checksum_sha256=checksum,
        )

    def download_file(self, object_key: str, destination: Path) -> StoredObject:
        key = _safe_object_key(object_key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            head = self.client.head_object(Bucket=self.bucket, Key=key)
            self.client.download_file(self.bucket, key, str(destination))
        except Exception as exc:
            raise StorageError("B2 download failed") from exc
        checksum = sha256_file(destination)
        expected = (head.get("Metadata") or {}).get("sha256")
        if expected and expected != checksum:
            destination.unlink(missing_ok=True)
            raise StorageError("B2 checksum verification failed")
        return StoredObject(
            provider=self.name,
            object_key=key,
            size_bytes=destination.stat().st_size,
            checksum_sha256=checksum,
        )

    def delete(self, object_key: str) -> None:
        key = _safe_object_key(object_key)
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
        except Exception as exc:
            raise StorageError("B2 delete failed") from exc

    def exists(self, object_key: str) -> bool:
        key = _safe_object_key(object_key)
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False

    def download_url(self, object_key: str) -> str:
        key = _safe_object_key(object_key)
        try:
            return self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=settings.b2_signed_url_expiry_seconds,
            )
        except Exception as exc:
            raise StorageError("B2 download URL generation failed") from exc


def get_storage(provider: str | None = None) -> StorageProvider:
    selected = (provider or settings.storage_provider).lower()
    if selected == "local":
        return LocalStorageProvider()
    if selected == "b2":
        return B2StorageProvider()
    raise StorageError(f"Unsupported storage provider: {selected}")


def materialize_asset(asset, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    if asset.storage_provider == "local":
        if not asset.local_path or not Path(asset.local_path).is_file():
            raise StorageError("Local asset file is missing")
        return Path(asset.local_path)
    if not asset.object_key:
        raise StorageError("Storage object key is missing")
    destination = destination_dir / Path(asset.original_filename).name
    get_storage(asset.storage_provider).download_file(asset.object_key, destination)
    return destination


def build_object_key(episode_id: str, version: int, filename: str, asset_type: str) -> str:
    safe = Path(filename).name.replace(" ", "_")
    return f"episodes/{episode_id}/assets/v{version}/{asset_type}/{safe}"
