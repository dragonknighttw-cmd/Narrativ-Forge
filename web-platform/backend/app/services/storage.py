from __future__ import annotations

import hashlib
import json
import shutil
import requests
from urllib.parse import urlparse
from dataclasses import dataclass
from pathlib import Path
from math import ceil
from uuid import UUID, uuid4
from typing import Protocol

from ..core.config import settings


class StorageError(RuntimeError):
    pass


class MultipartUploadAlreadyCompleted(StorageError):
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
    def initiate_multipart_upload(self, object_key: str, content_type: str, upload_token: str) -> str: ...
    def upload_part(
        self, upload_id: str, object_key: str, part_number: int, body: bytes, is_last: bool
    ) -> str: ...
    def list_multipart_parts(
        self,
        upload_id: str,
        object_key: str,
        upload_token: str | None = None,
        expected_size: int | None = None,
    ) -> list[dict]: ...
    def complete_multipart_upload(
        self,
        upload_id: str,
        object_key: str,
        parts: list[dict],
        expected_size: int,
        chunk_size: int,
        upload_token: str,
    ) -> StoredObject: ...
    def abort_multipart_upload(self, upload_id: str, object_key: str) -> None: ...


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()



def _hash_upload_token(upload_token: str) -> str:
    if not upload_token:
        raise StorageError("Multipart upload token is required")
    return hashlib.sha256(upload_token.encode("utf-8")).hexdigest()


def _cloudinary_download_url(url: str) -> str:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or hostname != "res.cloudinary.com":
        raise StorageError("Cloudinary returned an unexpected download host")
    return url

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
        self.multipart_root = self.root.parent / ".multipart"
        self.multipart_root.mkdir(parents=True, exist_ok=True)

    def _multipart_path(self, upload_id: str) -> Path:
        try:
            safe_id = str(UUID(upload_id))
        except ValueError as exc:
            raise StorageError("Invalid multipart upload identifier") from exc
        root = self.multipart_root.resolve()
        path = (root / safe_id).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise StorageError("Invalid multipart upload identifier") from exc
        return path

    def _multipart_metadata(self, upload_id: str, object_key: str) -> tuple[Path, dict]:
        directory = self._multipart_path(upload_id)
        metadata_path = directory / "metadata.json"
        if metadata_path.is_symlink():
            raise StorageError("Multipart upload metadata is invalid")
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise StorageError("Multipart upload not found") from exc
        if not isinstance(metadata, dict) or metadata.get("object_key") != _safe_object_key(object_key):
            raise StorageError("Multipart upload object key mismatch")
        return directory, metadata

    @staticmethod
    def _write_multipart_metadata(directory: Path, metadata: dict) -> None:
        temporary = directory / f".metadata-{uuid4().hex}.tmp"
        try:
            temporary.write_text(json.dumps(metadata), encoding="utf-8")
            temporary.replace(directory / "metadata.json")
        except OSError as exc:
            raise StorageError("Unable to persist multipart upload state") from exc
        finally:
            temporary.unlink(missing_ok=True)

    @staticmethod
    def _remove_multipart_parts(directory: Path) -> None:
        try:
            for part_path in directory.glob("part-*"):
                part_path.unlink()
        except OSError as exc:
            raise StorageError("Unable to clean up multipart parts") from exc

    def _path(self, object_key: str) -> Path:
        key = _safe_object_key(object_key)
        root = self.root.resolve()
        path = (root / key).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise StorageError("Invalid storage object key") from exc
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

    def initiate_multipart_upload(self, object_key: str, content_type: str, upload_token: str) -> str:
        key = _safe_object_key(object_key)
        if not upload_token:
            raise StorageError("Multipart upload token is required")
        upload_id = str(uuid4())
        directory = self._multipart_path(upload_id)
        directory.mkdir(parents=True, exist_ok=False)
        try:
            self._write_multipart_metadata(
                directory,
                {"object_key": key, "upload_token_hash": _hash_upload_token(upload_token), "status": "active"},
            )
        except StorageError:
            shutil.rmtree(directory, ignore_errors=True)
            raise
        return upload_id

    def upload_part(
        self, upload_id: str, object_key: str, part_number: int, body: bytes, is_last: bool
    ) -> str:
        if not 1 <= part_number <= 10_000:
            raise StorageError("Invalid multipart part number")
        if not body or len(body) > 5 * 1024 * 1024 * 1024:
            raise StorageError("Invalid multipart part size")
        directory, metadata = self._multipart_metadata(upload_id, object_key)
        if metadata.get("status") != "active":
            raise StorageError("Multipart upload is not active")
        part_path = directory / f"part-{part_number:05d}"
        temporary_path = directory / f".{part_path.name}.{uuid4().hex}.tmp"
        try:
            temporary_path.write_bytes(body)
            temporary_path.replace(part_path)
            return hashlib.md5(body, usedforsecurity=False).hexdigest()
        except OSError as exc:
            raise StorageError("Unable to persist multipart part") from exc
        finally:
            temporary_path.unlink(missing_ok=True)

    def list_multipart_parts(
        self,
        upload_id: str,
        object_key: str,
        upload_token: str | None = None,
        expected_size: int | None = None,
    ) -> list[dict]:
        directory, metadata = self._multipart_metadata(upload_id, object_key)
        if metadata.get("status") != "active":
            destination = self._path(object_key)
            if (
                metadata.get("status") == "completed"
                and upload_token
                and metadata.get("upload_token_hash") == _hash_upload_token(upload_token)
                and expected_size is not None
                and destination.is_file()
                and destination.stat().st_size == expected_size
            ):
                raise MultipartUploadAlreadyCompleted("Multipart upload already completed")
            return []
        parts = []
        for part_path in directory.glob("part-*"):
            if part_path.is_symlink():
                raise StorageError("Multipart part path is invalid")
            try:
                part_number = int(part_path.name.removeprefix("part-"))
            except ValueError:
                continue
            try:
                digest = hashlib.md5(usedforsecurity=False)
                with part_path.open("rb") as part_file:
                    while chunk := part_file.read(1024 * 1024):
                        digest.update(chunk)
                size = part_path.stat().st_size
            except OSError as exc:
                raise StorageError("Unable to inspect multipart part") from exc
            parts.append({
                "PartNumber": part_number,
                "Size": size,
                "ETag": digest.hexdigest(),
            })
        return sorted(parts, key=lambda part: part["PartNumber"])

    def complete_multipart_upload(
        self,
        upload_id: str,
        object_key: str,
        parts: list[dict],
        expected_size: int,
        chunk_size: int,
        upload_token: str,
    ) -> StoredObject:
        key = _safe_object_key(object_key)
        directory, metadata = self._multipart_metadata(upload_id, key)
        if metadata.get("upload_token_hash") != _hash_upload_token(upload_token):
            raise StorageError("Multipart upload token mismatch")
        destination = self._path(key)
        if metadata.get("status") == "completed":
            if not destination.is_file() or destination.stat().st_size != expected_size:
                raise StorageError("Completed multipart object is missing or has the wrong size")
            self._remove_multipart_parts(directory)
            return StoredObject(
                provider=self.name,
                object_key=key,
                size_bytes=expected_size,
                checksum_sha256=sha256_file(destination),
                local_path=str(destination),
            )

        if chunk_size <= 0 or expected_size <= 0:
            raise StorageError("Invalid multipart completion size")
        available = {part["PartNumber"]: part for part in self.list_multipart_parts(upload_id, key)}
        expected_count = (expected_size + chunk_size - 1) // chunk_size
        if (len(parts) != expected_count
            or set(available) != set(range(1, expected_count + 1))
            or [part.get("PartNumber") for part in parts] != list(range(1, expected_count + 1))
            or any(
                part.get("ETag") != available[number]["ETag"]
                or part.get("Size") != available[number]["Size"]
                or available[number]["Size"] != (
                    chunk_size if number < expected_count else expected_size - chunk_size * (expected_count - 1)
                )
                for number, part in enumerate(parts, start=1)
            )):
            raise StorageError("Multipart parts changed before completion")

        temporary = destination.with_name(f".{destination.name}.{upload_id}.tmp")
        digest = hashlib.sha256()
        size = 0
        try:
            with temporary.open("wb") as output:
                for part in parts:
                    part_path = directory / f"part-{part['PartNumber']:05d}"
                    with part_path.open("rb") as source:
                        while chunk := source.read(1024 * 1024):
                            output.write(chunk)
                            digest.update(chunk)
                            size += len(chunk)
            if size != expected_size:
                raise StorageError("Uploaded multipart size does not match the session")
            temporary.replace(destination)
        except OSError as exc:
            raise StorageError("Unable to complete local multipart upload") from exc
        finally:
            temporary.unlink(missing_ok=True)
        self._write_multipart_metadata(
            directory,
            {"object_key": key, "upload_token_hash": _hash_upload_token(upload_token), "status": "completed"},
        )
        self._remove_multipart_parts(directory)
        return StoredObject(
            provider=self.name,
            object_key=key,
            size_bytes=size,
            checksum_sha256=digest.hexdigest(),
            local_path=str(destination),
        )

    def abort_multipart_upload(self, upload_id: str, object_key: str) -> None:
        directory = self._multipart_path(upload_id)
        if not directory.exists():
            return
        directory, metadata = self._multipart_metadata(upload_id, object_key)
        if metadata.get("status") != "active":
            raise StorageError("Completed multipart upload cannot be aborted")
        try:
            shutil.rmtree(directory)
        except OSError as exc:
            raise StorageError("Unable to abort local multipart upload") from exc


class S3CompatibleStorageProvider:
    name = "b2"

    def __init__(
        self,
        *,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
        region: str,
        endpoint_url: str,
        signed_url_expiry_seconds: int,
    ):
        if not all([access_key_id, secret_access_key, bucket_name, region, endpoint_url]):
            raise StorageError(f"{self.name.upper()} storage is not configured")
        try:
            import boto3
            from botocore.config import Config
            from botocore.exceptions import ClientError
        except ImportError as exc:
            raise StorageError("boto3 is required for S3-compatible storage") from exc

        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region,
            config=Config(signature_version="s3v4"),
        )
        self._client_error = ClientError
        self.bucket = bucket_name
        self.signed_url_expiry_seconds = signed_url_expiry_seconds

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
                    "ServerSideEncryption": "AES256",
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
                ExpiresIn=self.signed_url_expiry_seconds,
            )
        except Exception as exc:
            raise StorageError("B2 download URL generation failed") from exc

    def initiate_multipart_upload(self, object_key: str, content_type: str, upload_token: str) -> str:
        key = _safe_object_key(object_key)
        if not upload_token:
            raise StorageError("Multipart upload token is required")
        try:
            response = self.client.create_multipart_upload(
                Bucket=self.bucket,
                Key=key,
                ContentType=content_type,
                Metadata={"nf-upload-session-hash": _hash_upload_token(upload_token)},
                ServerSideEncryption="AES256",
            )
            return response["UploadId"]
        except Exception as exc:
            raise StorageError("B2 multipart upload initialization failed") from exc

    def upload_part(
        self, upload_id: str, object_key: str, part_number: int, body: bytes, is_last: bool
    ) -> str:
        if not 1 <= part_number <= 10_000:
            raise StorageError("Invalid multipart part number")
        if not body or len(body) > 5 * 1024 * 1024 * 1024:
            raise StorageError("Invalid multipart part size")
        if not is_last and len(body) < 5 * 1024 * 1024:
            raise StorageError("Non-final B2 multipart parts must be at least 5 MiB")
        key = _safe_object_key(object_key)
        try:
            response = self.client.upload_part(
                Bucket=self.bucket,
                Key=key,
                UploadId=upload_id,
                PartNumber=part_number,
                Body=body,
            )
            return response["ETag"]
        except Exception as exc:
            raise StorageError("B2 multipart chunk upload failed") from exc

    def list_multipart_parts(
        self,
        upload_id: str,
        object_key: str,
        upload_token: str | None = None,
        expected_size: int | None = None,
    ) -> list[dict]:
        key = _safe_object_key(object_key)
        parts = []
        marker = 0
        try:
            while True:
                response = self.client.list_parts(
                    Bucket=self.bucket,
                    Key=key,
                    UploadId=upload_id,
                    PartNumberMarker=marker,
                )
                parts.extend(response.get("Parts", []))
                if not response.get("IsTruncated"):
                    return sorted(parts, key=lambda part: part["PartNumber"])
                next_marker = response.get("NextPartNumberMarker")
                if next_marker is None or next_marker <= marker:
                    raise StorageError("B2 returned an invalid multipart pagination marker")
                marker = next_marker
        except self._client_error as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            if code == "NoSuchUpload" and upload_token and expected_size is not None:
                completed = self._head_completed_object(key, expected_size, upload_token)
                if completed:
                    raise MultipartUploadAlreadyCompleted(
                        "Multipart upload already completed"
                    ) from exc
            raise StorageError("B2 multipart state lookup failed") from exc
        except Exception as exc:
            raise StorageError("B2 multipart state lookup failed") from exc

    def _head_completed_object(self, key: str, expected_size: int, upload_token: str) -> StoredObject | None:
        try:
            head = self.client.head_object(Bucket=self.bucket, Key=key)
        except self._client_error as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            if code in {"404", "NoSuchKey", "NotFound"}:
                return None
            raise StorageError("B2 multipart object lookup failed") from exc
        metadata = head.get("Metadata") or {}
        if metadata.get("nf-upload-session-hash") != _hash_upload_token(upload_token) or head.get("ContentLength") != expected_size:
            raise StorageError("B2 object does not match this upload session")
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            digest = hashlib.sha256()
            with response["Body"] as body:
                while chunk := body.read(1024 * 1024):
                    digest.update(chunk)
        except Exception as exc:
            raise StorageError("B2 completed object checksum verification failed") from exc
        return StoredObject(
            provider=self.name,
            object_key=key,
            size_bytes=expected_size,
            checksum_sha256=digest.hexdigest(),
        )

    def complete_multipart_upload(
        self,
        upload_id: str,
        object_key: str,
        parts: list[dict],
        expected_size: int,
        chunk_size: int,
        upload_token: str,
    ) -> StoredObject:
        key = _safe_object_key(object_key)
        try:
            already_completed = self._head_completed_object(key, expected_size, upload_token)
            if already_completed:
                return already_completed
            provider_parts = self.list_multipart_parts(upload_id, key)
            if chunk_size <= 0 or expected_size <= 0:
                raise StorageError("Invalid multipart completion size")
            expected_count = (expected_size + chunk_size - 1) // chunk_size
            if (
                len(parts) != expected_count
                or len(provider_parts) != expected_count
                or [part.get("PartNumber") for part in parts] != list(range(1, expected_count + 1))
                or [part.get("PartNumber") for part in provider_parts] != list(range(1, expected_count + 1))
                or any(
                    part.get("ETag") != provider_parts[number - 1].get("ETag")
                    or part.get("Size") != provider_parts[number - 1].get("Size")
                    or provider_parts[number - 1].get("Size") != (
                        chunk_size if number < expected_count else expected_size - chunk_size * (expected_count - 1)
                    )
                    for number, part in enumerate(parts, start=1)
                )
            ):
                raise StorageError("B2 multipart parts are incomplete or inconsistent")
            self.client.complete_multipart_upload(
                Bucket=self.bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={
                    "Parts": [
                        {"PartNumber": part["PartNumber"], "ETag": part["ETag"]}
                        for part in parts
                    ]
                },
            )
            completed = self._head_completed_object(key, expected_size, upload_token)
            if completed is None:
                raise StorageError("B2 completed object is missing")
            return completed
        except StorageError:
            raise
        except Exception as exc:
            raise StorageError("B2 multipart upload completion failed") from exc

    def abort_multipart_upload(self, upload_id: str, object_key: str) -> None:
        key = _safe_object_key(object_key)
        try:
            self.client.abort_multipart_upload(
                Bucket=self.bucket,
                Key=key,
                UploadId=upload_id,
            )
        except self._client_error as exc:
            code = str(exc.response.get("Error", {}).get("Code", ""))
            if code == "NoSuchUpload":
                return
            raise StorageError("B2 multipart upload abort failed") from exc
        except Exception as exc:
            raise StorageError("B2 multipart upload abort failed") from exc



class SupabaseStorageProvider:
    name = "supabase"

    def __init__(self):
        self.url = settings.supabase_url.rstrip("/")
        self.key = settings.supabase_service_role_key
        self.bucket = settings.supabase_storage_bucket
        self.signed_url_expiry_seconds = settings.supabase_signed_url_expiry_seconds
        if not self.url or not self.key or not self.bucket:
            raise StorageError("Supabase Storage is not configured")
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
        }
        self.multipart_root = Path(settings.upload_dir) / ".supabase-multipart"
        self.multipart_root.mkdir(parents=True, exist_ok=True)

    def _url(self, action: str, object_key: str = "") -> str:
        from urllib.parse import quote

        path = quote(_safe_object_key(object_key), safe="/") if object_key else ""
        if action:
            base = f"{self.url}/storage/v1/object/{action}/{self.bucket}"
        else:
            base = f"{self.url}/storage/v1/object/{self.bucket}"
        return f"{base}/{path}" if path else base

    def upload_file(self, source: Path, object_key: str, content_type: str) -> StoredObject:
        key = _safe_object_key(object_key)
        checksum = sha256_file(source)
        try:
            with source.open("rb") as handle:
                response = requests.post(
                    self._url("", key),
                    headers={**self.headers, "Content-Type": content_type, "x-upsert": "true"},
                    data=handle,
                    timeout=300,
                )
            response.raise_for_status()
        except Exception as exc:
            raise StorageError("Supabase Storage upload failed") from exc
        return StoredObject(provider=self.name, object_key=key, size_bytes=source.stat().st_size, checksum_sha256=checksum)

    def download_file(self, object_key: str, destination: Path) -> StoredObject:
        key = _safe_object_key(object_key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            response = requests.get(self._url("", key), headers=self.headers, timeout=300, stream=True)
            response.raise_for_status()
            with destination.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
        except Exception as exc:
            destination.unlink(missing_ok=True)
            raise StorageError("Supabase Storage download failed") from exc
        checksum = sha256_file(destination)
        return StoredObject(provider=self.name, object_key=key, size_bytes=destination.stat().st_size, checksum_sha256=checksum)

    def delete(self, object_key: str) -> None:
        key = _safe_object_key(object_key)
        try:
            response = requests.delete(
                f"{self.url}/storage/v1/object/{self.bucket}",
                headers={**self.headers, "Content-Type": "application/json"},
                json={"prefixes": [key]},
                timeout=60,
            )
            if not response.ok:
                raise StorageError(f"Supabase Storage delete failed: HTTP {response.status_code} {response.text[:300]}")
        except StorageError:
            raise
        except Exception as exc:
            raise StorageError("Supabase Storage delete failed") from exc

    def exists(self, object_key: str) -> bool:
        key = _safe_object_key(object_key)
        try:
            response = requests.head(self._url("", key), headers=self.headers, timeout=30)
            return response.status_code == 200
        except Exception:
            return False

    def download_url(self, object_key: str) -> str:
        key = _safe_object_key(object_key)
        try:
            response = requests.post(
                f"{self.url}/storage/v1/object/sign/{self.bucket}/{key}",
                headers={**self.headers, "Content-Type": "application/json"},
                json={"expiresIn": self.signed_url_expiry_seconds},
                timeout=30,
            )
            response.raise_for_status()
            signed = response.json().get("signedURL") or response.json().get("signedUrl")
            if not signed:
                raise StorageError("Supabase Storage did not return a signed URL")
            return signed if signed.startswith("http") else f"{self.url}/storage/v1{signed}"
        except StorageError:
            raise
        except Exception as exc:
            raise StorageError("Supabase Storage signed URL generation failed") from exc

    def _dir(self, upload_id: str) -> Path:
        try:
            safe_id = str(UUID(upload_id))
        except ValueError as exc:
            raise StorageError("Invalid multipart upload identifier") from exc
        root = self.multipart_root.resolve()
        directory = (root / safe_id).resolve()
        try:
            directory.relative_to(root)
        except ValueError as exc:
            raise StorageError("Invalid multipart upload identifier") from exc
        return directory

    def _meta(self, upload_id: str, object_key: str) -> tuple[Path, dict]:
        directory = self._dir(upload_id)
        try:
            metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise StorageError("Supabase multipart upload not found") from exc
        if metadata.get("object_key") != _safe_object_key(object_key):
            raise StorageError("Supabase multipart object key mismatch")
        return directory, metadata

    def initiate_multipart_upload(self, object_key: str, content_type: str, upload_token: str) -> str:
        if not upload_token:
            raise StorageError("Multipart upload token is required")
        upload_id = str(uuid4())
        directory = self._dir(upload_id)
        directory.mkdir(parents=True, exist_ok=False)
        (directory / "metadata.json").write_text(json.dumps({
            "object_key": _safe_object_key(object_key),
            "content_type": content_type,
            "upload_token": upload_token,
            "status": "active",
        }), encoding="utf-8")
        return upload_id

    def upload_part(self, upload_id: str, object_key: str, part_number: int, body: bytes, is_last: bool) -> str:
        if not 1 <= part_number <= 10_000 or not body:
            raise StorageError("Invalid multipart part")
        directory, metadata = self._meta(upload_id, object_key)
        if metadata.get("status") != "active":
            raise StorageError("Multipart upload is not active")
        part = directory / f"part-{part_number:05d}"
        temporary = directory / f".{part.name}.{uuid4().hex}.tmp"
        try:
            temporary.write_bytes(body)
            temporary.replace(part)
            return hashlib.md5(body, usedforsecurity=False).hexdigest()
        except OSError as exc:
            raise StorageError("Unable to persist Supabase multipart part") from exc
        finally:
            temporary.unlink(missing_ok=True)

    def list_multipart_parts(self, upload_id: str, object_key: str, upload_token: str | None = None, expected_size: int | None = None) -> list[dict]:
        directory, metadata = self._meta(upload_id, object_key)
        if upload_token and metadata.get("upload_token_hash") != _hash_upload_token(upload_token):
            raise StorageError("Multipart upload token mismatch")
        parts = []
        for path in directory.glob("part-*"):
            try:
                number = int(path.name.removeprefix("part-"))
                size = path.stat().st_size
            except (ValueError, OSError):
                continue
            digest = hashlib.md5(usedforsecurity=False)
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            parts.append({"PartNumber": number, "Size": size, "ETag": digest.hexdigest()})
        return sorted(parts, key=lambda item: item["PartNumber"])

    def complete_multipart_upload(self, upload_id: str, object_key: str, parts: list[dict], expected_size: int, chunk_size: int, upload_token: str) -> StoredObject:
        directory, metadata = self._meta(upload_id, object_key)
        if metadata.get("upload_token_hash") != _hash_upload_token(upload_token):
            raise StorageError("Multipart upload token mismatch")
        expected_parts = ceil(expected_size / chunk_size)
        available = {part["PartNumber"]: part for part in self.list_multipart_parts(upload_id, object_key)}
        if len(parts) != expected_parts or set(available) != set(range(1, expected_parts + 1)):
            raise StorageError("Multipart upload is incomplete")
        for part in parts:
            remote = available.get(part.get("PartNumber"))
            if not remote or remote["ETag"] != part.get("ETag") or remote["Size"] != part.get("Size"):
                raise StorageError("Multipart parts changed before completion")
        temporary = directory / "assembled.tmp"
        checksum = hashlib.sha256()
        size = 0
        try:
            with temporary.open("wb") as output:
                for part in parts:
                    source = directory / f"part-{part['PartNumber']:05d}"
                    with source.open("rb") as handle:
                        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                            output.write(chunk)
                            checksum.update(chunk)
                            size += len(chunk)
            if size != expected_size:
                raise StorageError("Supabase multipart size mismatch")
            stored = self.upload_file(temporary, object_key, metadata["content_type"])
        except OSError as exc:
            raise StorageError("Unable to assemble Supabase multipart upload") from exc
        finally:
            shutil.rmtree(directory, ignore_errors=True)
        return stored

    def abort_multipart_upload(self, upload_id: str, object_key: str) -> None:
        directory = self._dir(upload_id)
        if directory.exists():
            self._meta(upload_id, object_key)
            shutil.rmtree(directory, ignore_errors=True)


class CloudinaryStorageProvider:
    name = "cloudinary"
    def __init__(self):
        try:
            import cloudinary
            import cloudinary.uploader
            import cloudinary.utils
        except ImportError as exc:
            raise StorageError("cloudinary package is required for Cloudinary storage") from exc
        if not all([settings.cloudinary_cloud_name, settings.cloudinary_api_key, settings.cloudinary_api_secret]):
            raise StorageError("Cloudinary storage is not configured")
        cloudinary.config(cloud_name=settings.cloudinary_cloud_name, api_key=settings.cloudinary_api_key, api_secret=settings.cloudinary_api_secret, secure=True)
        self.cloudinary = cloudinary
        self.uploader = cloudinary.uploader
        self.utils = cloudinary.utils
        self.multipart_root = Path(settings.upload_dir) / ".cloudinary-multipart"
        self.multipart_root.mkdir(parents=True, exist_ok=True)
    @staticmethod
    def _resource_type(object_key: str) -> str:
        return "video" if Path(object_key).suffix.lower() in {".mp4", ".webm", ".mov", ".mp3", ".wav", ".m4a"} else "raw"
    @staticmethod
    def _public_id(object_key: str) -> str:
        return _safe_object_key(object_key).rsplit(".", 1)[0]
    def upload_file(self, source: Path, object_key: str, content_type: str) -> StoredObject:
        key = _safe_object_key(object_key)
        kwargs = {"resource_type": self._resource_type(key), "public_id": self._public_id(key), "overwrite": True, "invalidate": True}
        try:
            self.uploader.upload_large(str(source), chunk_size=settings.cloudinary_chunk_size_bytes, **kwargs) if source.stat().st_size > 100 * 1024 * 1024 else self.uploader.upload(str(source), **kwargs)
        except Exception as exc:
            raise StorageError("Cloudinary upload failed") from exc
        return StoredObject(provider=self.name, object_key=key, size_bytes=source.stat().st_size, checksum_sha256=sha256_file(source))
    def download_file(self, object_key: str, destination: Path) -> StoredObject:
        key = _safe_object_key(object_key)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            download_url = _cloudinary_download_url(self.download_url(key))
            response = requests.get(download_url, timeout=300, stream=True)
            response.raise_for_status()
            with destination.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
        except Exception as exc:
            raise StorageError("Cloudinary download failed") from exc
        return StoredObject(provider=self.name, object_key=key, size_bytes=destination.stat().st_size, checksum_sha256=sha256_file(destination))
    def delete(self, object_key: str) -> None:
        key = _safe_object_key(object_key)
        try:
            self.uploader.destroy(self._public_id(key), resource_type=self._resource_type(key), type="upload", invalidate=True)
        except Exception as exc:
            raise StorageError("Cloudinary delete failed") from exc
    def exists(self, object_key: str) -> bool:
        key = _safe_object_key(object_key)
        try:
            self.cloudinary.api.resource(self._public_id(key), resource_type=self._resource_type(key), type="upload")
            return True
        except Exception:
            return False
    def download_url(self, object_key: str) -> str | None:
        key = _safe_object_key(object_key)
        try:
            url, _ = self.utils.cloudinary_url(self._public_id(key), resource_type=self._resource_type(key), type="upload", secure=True, sign_url=True)
            return url
        except Exception as exc:
            raise StorageError("Cloudinary URL generation failed") from exc
    def _multipart_dir(self, upload_id: str) -> Path:
        try:
            safe_id = str(UUID(upload_id))
        except ValueError as exc:
            raise StorageError("Invalid multipart upload identifier") from exc
        root = self.multipart_root.resolve()
        path = (root / safe_id).resolve()
        path.relative_to(root)
        return path
    def initiate_multipart_upload(self, object_key: str, content_type: str, upload_token: str) -> str:
        upload_id = str(uuid4())
        directory = self._multipart_dir(upload_id)
        directory.mkdir(parents=True, exist_ok=False)
        (directory / "metadata.json").write_text(json.dumps({"object_key": _safe_object_key(object_key), "upload_token_hash": _hash_upload_token(upload_token), "content_type": content_type}), encoding="utf-8")
        return upload_id
    def upload_part(self, upload_id: str, object_key: str, part_number: int, body: bytes, is_last: bool) -> str:
        directory = self._multipart_dir(upload_id)
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        if metadata.get("object_key") != _safe_object_key(object_key):
            raise StorageError("Multipart upload object key mismatch")
        (directory / f"part-{part_number:05d}").write_bytes(body)
        return hashlib.md5(body, usedforsecurity=False).hexdigest()
    def list_multipart_parts(self, upload_id: str, object_key: str, upload_token: str | None = None, expected_size: int | None = None) -> list[dict]:
        directory = self._multipart_dir(upload_id)
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        if metadata.get("object_key") != _safe_object_key(object_key):
            raise StorageError("Multipart upload object key mismatch")
        if upload_token and metadata.get("upload_token_hash") != _hash_upload_token(upload_token):
            raise StorageError("Multipart upload token mismatch")
        result = []
        for path in sorted(directory.glob("part-*")):
            data = path.read_bytes()
            result.append({"PartNumber": int(path.name.removeprefix("part-")), "Size": len(data), "ETag": hashlib.md5(data, usedforsecurity=False).hexdigest()})
        return result
    def complete_multipart_upload(self, upload_id: str, object_key: str, parts: list[dict], expected_size: int, chunk_size: int, upload_token: str) -> StoredObject:
        directory = self._multipart_dir(upload_id)
        metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        if metadata.get("object_key") != _safe_object_key(object_key) or metadata.get("upload_token_hash") != _hash_upload_token(upload_token):
            raise StorageError("Multipart upload authorization failed")
        expected_count = ceil(expected_size / chunk_size)
        if len(parts) != expected_count:
            raise StorageError("Multipart parts are incomplete")
        temporary = directory / "combined.tmp"
        digest = hashlib.sha256()
        size = 0
        try:
            with temporary.open("wb") as output:
                for number in range(1, expected_count + 1):
                    path = directory / f"part-{number:05d}"
                    if not path.is_file():
                        raise StorageError("Multipart part is missing")
                    data = path.read_bytes()
                    expected = parts[number - 1]
                    if expected.get("PartNumber") != number or expected.get("Size") != len(data) or expected.get("ETag") != hashlib.md5(data, usedforsecurity=False).hexdigest():
                        raise StorageError("Multipart part changed before completion")
                    output.write(data)
                    digest.update(data)
                    size += len(data)
            if size != expected_size:
                raise StorageError("Multipart size mismatch")
            self.upload_file(temporary, object_key, metadata.get("content_type", "application/octet-stream"))
        finally:
            shutil.rmtree(directory, ignore_errors=True)
        return StoredObject(provider=self.name, object_key=_safe_object_key(object_key), size_bytes=size, checksum_sha256=digest.hexdigest())
    def abort_multipart_upload(self, upload_id: str, object_key: str) -> None:
        directory = self._multipart_dir(upload_id)
        if directory.exists():
            shutil.rmtree(directory, ignore_errors=True)

class B2StorageProvider(S3CompatibleStorageProvider):
    name = "b2"

    def __init__(self):
        super().__init__(
            access_key_id=settings.b2_application_key_id,
            secret_access_key=settings.b2_application_key,
            bucket_name=settings.b2_bucket_name,
            region=settings.b2_region,
            endpoint_url=settings.b2_endpoint_url or f"https://s3.{settings.b2_region}.backblazeb2.com",
            signed_url_expiry_seconds=settings.b2_signed_url_expiry_seconds,
        )



def get_storage(provider: str | None = None) -> StorageProvider:
    selected = (provider or settings.storage_provider).lower()
    if selected == "local":
        return LocalStorageProvider()
    if selected == "b2":
        return B2StorageProvider()
    if selected == "cloudinary":
        return CloudinaryStorageProvider()
    if selected == "supabase":
        return SupabaseStorageProvider()
    raise StorageError(f"Unsupported storage provider: {selected}")


def storage_provider_for_asset(asset_type: str, size_bytes: int, content_type: str | None = None) -> str:
    """Choose durable storage by media role; local mode remains deterministic for development and CI."""
    if settings.storage_provider.lower() == "local":
        return "local"
    kind = (asset_type or "").lower()
    mime = (content_type or "").lower()
    if kind in {"video", "audio"} or mime.startswith(("video/", "audio/")):
        return "b2"
    if kind in {"thumbnail", "cover", "image", "srt_preview"} and size_bytes <= 10 * 1024 * 1024:
        return "cloudinary"
    if size_bytes <= 50 * 1024 * 1024:
        return "supabase"
    return "b2"


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
