import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import get_db
from ...models import Asset, Episode, ExportRecord, Subtitle
from ...services.audit import record_event
from ...services.storage import StorageError, materialize_asset
from ..dependencies import get_current_user, require_roles

router = APIRouter(prefix="/episodes", tags=["export"])


def _episode(db, episode_id):
    item = db.get(Episode, episode_id)
    if not item:
        raise HTTPException(status_code=404, detail="Episode not found")
    return item


def _record(db, episode_id: str, provider: str):
    return db.query(ExportRecord).filter(
        ExportRecord.episode_id == episode_id,
        ExportRecord.provider == provider,
    ).first()


def _manifest(record: ExportRecord) -> dict:
    return json.loads(record.manifest_json or "{}")


@router.get("/{episode_id}/export")
def get_export(episode_id: str, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _episode(db, episode_id)
    item = _record(db, episode_id, "mock_drive")
    if not item:
        return {"status": "not_exported", "episode_id": episode_id}
    return {
        "id": item.id,
        "episode_id": item.episode_id,
        "provider": item.provider,
        "status": item.status,
        "manifest": _manifest(item),
        "drive_folder_id": item.drive_folder_id,
        "drive_file_id": item.drive_file_id,
        "error_code": item.error_code,
        "error_message": item.error_message,
        "completed_at": item.completed_at,
    }


@router.get("/{episode_id}/export/history")
def export_history(episode_id: str, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _episode(db, episode_id)
    records = db.query(ExportRecord).filter(
        ExportRecord.episode_id == episode_id
    ).order_by(ExportRecord.created_at.desc()).all()
    return [{
        "id": item.id,
        "provider": item.provider,
        "status": item.status,
        "manifest": _manifest(item),
        "drive_folder_id": item.drive_folder_id,
        "drive_file_id": item.drive_file_id,
        "error_code": item.error_code,
        "error_message": item.error_message,
        "created_at": item.created_at,
        "completed_at": item.completed_at,
    } for item in records]


@router.post("/{episode_id}/export/mock-drive")
def mock_drive_export(episode_id: str, user=Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    episode = _episode(db, episode_id)
    record = _record(db, episode_id, "mock_drive")
    if record and record.status == "completed":
        return {"status": "completed", "id": record.id, "manifest": _manifest(record)}
    if episode.status != "approved":
        raise HTTPException(status_code=409, detail="Episode must be approved before Drive export")

    subtitle = db.query(Subtitle).filter(
        Subtitle.episode_id == episode_id,
        Subtitle.is_current.is_(True),
        Subtitle.status == "approved",
    ).first()
    final_asset = db.query(Asset).filter(
        Asset.episode_id == episode_id,
        Asset.is_final.is_(True),
    ).order_by(Asset.version.desc()).first()
    if not final_asset:
        raise HTTPException(status_code=422, detail="Approved final video asset is missing")
    if not subtitle:
        raise HTTPException(status_code=422, detail="Approved subtitle is missing")

    try:
        with tempfile.TemporaryDirectory(prefix="nf-export-") as work:
            source = materialize_asset(final_asset, Path(work))
            export_root = Path(settings.upload_dir) / "mock_drive" / episode.public_id
            export_root.mkdir(parents=True, exist_ok=True)
            destination = export_root / Path(final_asset.original_filename).name
            shutil.copy2(source, destination)
    except StorageError as exc:
        raise HTTPException(status_code=502, detail="Approved final video could not be read from storage") from exc
    manifest = {
        "episode_public_id": episode.public_id,
        "episode_id": episode.id,
        "provider": "mock_drive",
        "video_asset_id": final_asset.id,
        "video_object_key": final_asset.object_key,
        "video_checksum_sha256": final_asset.checksum_sha256,
        "subtitle_id": subtitle.id,
        "subtitle_version": subtitle.version,
        "video_filename": destination.name,
        "subtitle_formats": ["srt", "vtt"],
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }
    if not record:
        record = ExportRecord(episode_id=episode_id, provider="mock_drive")
        db.add(record)
    record.status = "completed"
    record.manifest_json = json.dumps(manifest, ensure_ascii=False)
    record.drive_folder_id = f"mock-folder-{episode.public_id}"
    record.drive_file_id = f"mock-file-{final_asset.id}"
    record.error_code = None
    record.error_message = None
    record.completed_at = datetime.now(timezone.utc)
    episode.status = "exported"
    episode.current_step = "output"
    record_event(db, actor_email=user["email"], action="episode.exported", resource_type="episode", resource_id=episode.id, metadata={"provider": "mock_drive", "export_id": record.id, "video_asset_id": final_asset.id})
    db.commit()
    return {"status": "completed", "id": record.id, "manifest": manifest, "mock_path": str(destination)}


@router.post("/{episode_id}/export/google-drive")
async def google_drive_export(episode_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)):
    from .google_drive import access_token_for
    from ...services.subtitles import render_srt

    episode = _episode(db, episode_id)
    record = _record(db, episode_id, "google_drive")
    retrying_failed_export = bool(record and record.status == "failed" and episode.status == "failed")
    if record and record.status == "completed":
        return {"status": "completed", "id": record.id, "manifest": _manifest(record)}
    if episode.status != "approved" and not retrying_failed_export:
        raise HTTPException(status_code=409, detail="Episode must be approved before Drive export")

    subtitle = db.query(Subtitle).filter(
        Subtitle.episode_id == episode_id,
        Subtitle.is_current.is_(True),
        Subtitle.status == "approved",
    ).first()
    final_asset = db.query(Asset).filter(
        Asset.episode_id == episode_id,
        Asset.is_final.is_(True),
    ).order_by(Asset.version.desc()).first()
    if not final_asset:
        raise HTTPException(status_code=422, detail="Approved final video asset is missing")
    if not subtitle:
        raise HTTPException(status_code=422, detail="Approved subtitle is missing")

    export_temp = tempfile.TemporaryDirectory(prefix="nf-drive-export-")
    try:
        local_final = materialize_asset(final_asset, Path(export_temp.name))
        token = await access_token_for(user["email"], db)
        episode.status = "exporting"
        if not record:
            record = ExportRecord(episode_id=episode_id, provider="google_drive")
            db.add(record)
        record.status = "running"
        record.error_code = None
        record.error_message = None
        db.commit()

        async with httpx.AsyncClient(timeout=60) as client:
            headers = {"Authorization": f"Bearer {token}"}
            existing_manifest = _manifest(record)
            folder_id = record.drive_folder_id or existing_manifest.get("folder_id")
            if not folder_id:
                folder_response = await client.post(
                    "https://www.googleapis.com/drive/v3/files",
                    headers=headers,
                    json={"name": episode.public_id, "mimeType": "application/vnd.google-apps.folder"},
                )
                folder_response.raise_for_status()
                folder_id = folder_response.json()["id"]
                record.drive_folder_id = folder_id
                existing_manifest["folder_id"] = folder_id
                record.manifest_json = json.dumps(existing_manifest, ensure_ascii=False)
                db.commit()

            async def find_child(name):
                safe_name = name.replace("'", "\\'")
                query = "name = '" + safe_name + "' and '" + folder_id + "' in parents and trashed = false"
                response = await client.get(
                    "https://www.googleapis.com/drive/v3/files",
                    headers=headers,
                    params={"q": query, "pageSize": 1, "fields": "files(id,name)"},
                )
                response.raise_for_status()
                files = response.json().get("files", [])
                return files[0]["id"] if files else None

            async def upload_bytes(name, mime, data, existing_id=None):
                if existing_id:
                    return existing_id
                found_id = await find_child(name)
                if found_id:
                    return found_id
                boundary = "narrativforgeboundary"
                metadata = json.dumps({"name": name, "parents": [folder_id]})
                body = (
                    f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{metadata}\r\n"
                    f"--{boundary}\r\nContent-Type: {mime}\r\n\r\n"
                ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
                response = await client.post(
                    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                    headers={**headers, "Content-Type": f"multipart/related; boundary={boundary}"},
                    content=body,
                )
                response.raise_for_status()
                return response.json()["id"]

            video_name = Path(final_asset.original_filename).name
            video_id = await upload_bytes(
                video_name,
                final_asset.mime_type,
                local_final.read_bytes(),
                record.drive_file_id,
            )
            record.drive_file_id = video_id
            manifest = _manifest(record)
            manifest.update({
                "episode_public_id": episode.public_id,
                "episode_id": episode.id,
                "provider": "google_drive",
                "folder_id": folder_id,
                "video_file_id": video_id,
                "video_object_key": final_asset.object_key,
                "video_checksum_sha256": final_asset.checksum_sha256,
                "subtitle_version": subtitle.version,
            })
            record.manifest_json = json.dumps(manifest, ensure_ascii=False)
            db.commit()

            srt_id = await upload_bytes(
                f"{episode.public_id}.srt",
                "application/x-subrip",
                render_srt(json.loads(subtitle.cues_json or "[]")).encode("utf-8"),
                manifest.get("subtitle_file_id"),
            )
            manifest["subtitle_file_id"] = srt_id
            record.manifest_json = json.dumps(manifest, ensure_ascii=False)
            db.commit()

            manifest_payload = json.dumps({
                **manifest,
                "exported_at": datetime.now(timezone.utc).isoformat(),
            }, ensure_ascii=False, indent=2).encode("utf-8")
            manifest_id = await upload_bytes(
                f"{episode.public_id}-export-manifest.json",
                "application/json",
                manifest_payload,
                manifest.get("manifest_file_id"),
            )
            manifest["manifest_file_id"] = manifest_id

        manifest["exported_at"] = datetime.now(timezone.utc).isoformat()
        record.status = "completed"
        record.manifest_json = json.dumps(manifest, ensure_ascii=False)
        record.drive_folder_id = folder_id
        record.drive_file_id = video_id
        record.completed_at = datetime.now(timezone.utc)
        episode.status = "exported"
        episode.current_step = "output"
        record_event(db, actor_email=user["email"], action="episode.exported", resource_type="episode", resource_id=episode.id, metadata={"provider": "google_drive", "export_id": record.id, "video_file_id": video_id, "folder_id": folder_id})
        db.commit()
        return {"status": "completed", "id": record.id, "manifest": manifest}
    except StorageError as exc:
        if record:
            record.status = "failed"
            record.error_code = "DRIVE_STORAGE_ERROR"
            record.error_message = "Google Drive export could not read the approved storage object."
            episode.status = "failed"
            episode.current_step = "processing"
            db.commit()
        raise HTTPException(status_code=502, detail="Drive export could not read the approved storage object; retry is safe.") from exc
    except httpx.HTTPError as exc:
        if record:
            record.status = "failed"
            record.error_code = "DRIVE_API_ERROR"
            record.error_message = "Google Drive export failed."
            episode.status = "failed"
            episode.current_step = "processing"
            db.commit()
        raise HTTPException(status_code=502, detail="Google Drive export failed; retry is safe.") from exc
    except OSError as exc:
        if record:
            record.status = "failed"
            record.error_code = "DRIVE_FILE_ERROR"
            record.error_message = "Google Drive export could not read the local output."
            episode.status = "failed"
            episode.current_step = "processing"
            db.commit()
        raise HTTPException(status_code=500, detail="Drive export could not read the local output; retry is safe.") from exc
    finally:
        export_temp.cleanup()
