from pathlib import Path
import re
import tempfile
import hashlib
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import get_db
from ...models import Asset, Episode, Scene, UploadSession
from ...middleware.idempotency import (
    IdempotencyClaim,
    StoredResponse,
    begin_idempotency,
    complete_idempotency,
    request_fingerprint,
    validate_idempotency_key,
)
from ...services.storage import StorageError, build_object_key, get_storage, storage_provider_for_asset
from ..dependencies import get_current_membership, get_current_user, require_roles

router = APIRouter(prefix="/episodes", tags=["assets"])
asset_router = APIRouter(prefix="/assets", tags=["assets"])

ALLOWED_TYPES = {
    "video": {"video/mp4", "video/webm", "video/quicktime"},
    "audio": {"audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4"},
    "image": {"image/jpeg", "image/png", "image/webp"},
    "thumbnail": {"image/jpeg", "image/png", "image/webp"},
    "cover": {"image/jpeg", "image/png", "image/webp"},
    "srt_preview": {"text/plain", "application/x-subrip"},
    "srt": {"text/plain", "application/x-subrip"},
    "manifest": {"application/json", "text/plain"},
}
SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


class AssetUpdate(BaseModel):
    scene_id: str | None = None
    copyright_status: str | None = Field(default=None, max_length=40)
    status: str | None = Field(default=None, max_length=40)
    is_final: bool | None = None


def safe_filename(name: str) -> str:
    base = Path(name or "upload.bin").name
    cleaned = SAFE_NAME.sub("_", base).strip("._")
    return (cleaned or "upload.bin")[:180]


def validate_upload(filename: str, content_type: str | None, asset_type: str) -> None:
    if asset_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported asset type")
    suffix = Path(filename).suffix.lower()
    if not content_type or content_type not in ALLOWED_TYPES[asset_type]:
        raise HTTPException(status_code=415, detail="Unsupported file MIME type")
    suffixes = {
        "image": {".jpg", ".jpeg", ".png", ".webp"},
        "thumbnail": {".jpg", ".jpeg", ".png", ".webp"},
        "cover": {".jpg", ".jpeg", ".png", ".webp"},
        "srt_preview": {".srt", ".txt"},
        "srt": {".srt", ".txt"},
        "manifest": {".json", ".txt"},
        "video": {".mp4", ".webm", ".mov"},
        "audio": {".mp3", ".wav", ".m4a"},
    }
    if suffix not in suffixes[asset_type]:
        raise HTTPException(status_code=415, detail="Unsupported file extension")


def _episode_or_404(db: Session, episode_id: str, organization_id: str | None = None) -> Episode:
    item = db.query(Episode).filter(Episode.id == episode_id, *( [Episode.organization_id == organization_id] if organization_id else [] )).first()
    if not item:
        raise HTTPException(status_code=404, detail="Episode not found")
    return item


@router.get("/{episode_id}/assets")
def list_assets(episode_id: str, membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id, membership.organization_id)
    return db.query(Asset).filter(Asset.episode_id == episode_id).order_by(Asset.created_at.desc()).all()


@router.post("/{episode_id}/assets/upload", status_code=201)
async def upload_asset(
    episode_id: str,
    request: Request,
    file: UploadFile = File(...),
    asset_type: str = Form(...),
    scene_id: str | None = Form(default=None),
    copyright_status: str = Form(default="unknown"),
    checksum_header: str | None = Header(default=None, alias="X-Content-SHA256"),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    user: dict = Depends(require_roles("owner", "editor")),
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    idempotency_key = validate_idempotency_key(idempotency_key)
    episode = db.query(Episode).filter(Episode.id == episode_id, Episode.organization_id == membership.organization_id).with_for_update().first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    validate_upload(file.filename or "", file.content_type, asset_type)
    if scene_id:
        scene = db.query(Scene).join(Episode, Scene.episode_id == Episode.id).filter(Scene.id == scene_id, Episode.organization_id == membership.organization_id).first()
        if not scene or scene.episode_id != episode_id:
            raise HTTPException(status_code=422, detail="Scene does not belong to this episode")

    asset_version = db.query(func.max(Asset.version)).filter(Asset.episode_id == episode_id).scalar() or 0
    reserved_version = db.query(func.max(UploadSession.reserved_version)).filter(
        UploadSession.episode_id == episode_id,
    ).scalar() or 0
    version = max(asset_version, reserved_version) + 1
    safe_name = safe_filename(file.filename or "upload.bin")
    object_key = build_object_key(episode_id, version, f"{uuid4().hex}_{safe_name}", asset_type)

    temp_path = None
    digest = hashlib.sha256()
    try:
        with tempfile.NamedTemporaryFile(prefix="nf-upload-", suffix=Path(safe_name).suffix, delete=False) as temp:
            temp_path = Path(temp.name)
            size = 0
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_upload_size_bytes:
                    raise HTTPException(status_code=413, detail="File exceeds upload size limit")
                digest.update(chunk)
                temp.write(chunk)

        checksum = digest.hexdigest()
        if checksum_header is not None:
            checksum_header = checksum_header.strip().lower()
            if not re.fullmatch(r"[0-9a-f]{64}", checksum_header):
                raise HTTPException(status_code=422, detail="Invalid X-Content-SHA256 checksum")
            if checksum_header != checksum:
                raise HTTPException(status_code=422, detail="X-Content-SHA256 does not match uploaded content")

        claim_or_response = begin_idempotency(
            db,
            actor_id=user["id"],
            key=idempotency_key,
            method=request.method,
            target=request.url.path,
            fingerprint=request_fingerprint(
                request.method,
                request.url.path,
                {
                    "episode_id": episode_id,
                    "filename": safe_name,
                    "mime_type": file.content_type,
                    "asset_type": asset_type,
                    "scene_id": scene_id,
                    "copyright_status": copyright_status,
                    "size_bytes": size,
                    "sha256": checksum,
                },
            ),
            resource_type="asset",
        )
        if isinstance(claim_or_response, StoredResponse):
            return claim_or_response.response()
        if isinstance(claim_or_response, IdempotencyClaim) and not claim_or_response.created:
            raise HTTPException(status_code=409, detail="Asset upload request is still processing")
        claim = claim_or_response if isinstance(claim_or_response, IdempotencyClaim) else None

        existing = db.query(Asset).filter(
            Asset.checksum_sha256 == checksum,
            Asset.asset_type == asset_type,
            Asset.status != "deleted",
        ).order_by(Asset.created_at.asc()).first()
        if existing:
            if existing.episode_id == episode_id:
                if claim:
                    claim.record.resource_id = existing.id
                    stored_response = complete_idempotency(claim, jsonable_encoder(existing), status_code=201)
                    db.commit()
                    if stored_response:
                        return stored_response.response()
                return existing

            item = Asset(
                id=claim.record.resource_id if claim else str(uuid4()),
                episode_id=episode_id,
                scene_id=scene_id,
                asset_type=asset_type,
                original_filename=safe_name,
                storage_provider=existing.storage_provider,
                local_path=existing.local_path,
                object_key=existing.object_key,
                checksum_sha256=existing.checksum_sha256,
                mime_type=file.content_type or existing.mime_type,
                file_size_bytes=existing.file_size_bytes,
                version=version,
                copyright_status=copyright_status,
                status="uploaded",
            )
            db.add(item)
            db.flush()
            stored_response = complete_idempotency(claim, jsonable_encoder(item), status_code=201)
            db.commit()
            if stored_response:
                return stored_response.response()
            db.refresh(item)
            return item

        selected_provider = storage_provider_for_asset(asset_type, size, file.content_type)
        stored = get_storage(selected_provider).upload_file(temp_path, object_key, file.content_type or "application/octet-stream")
    except HTTPException:
        raise
    except StorageError as exc:
        raise HTTPException(status_code=502, detail="Unable to store upload") from exc
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)

    item = Asset(
        id=claim.record.resource_id if claim else str(uuid4()),
        episode_id=episode_id,
        scene_id=scene_id,
        asset_type=asset_type,
        original_filename=safe_name,
        storage_provider=stored.provider,
        local_path=stored.local_path,
        object_key=stored.object_key,
        checksum_sha256=stored.checksum_sha256,
        mime_type=file.content_type or "application/octet-stream",
        file_size_bytes=stored.size_bytes,
        version=version,
        copyright_status=copyright_status,
        status="uploaded",
    )
    db.add(item)
    db.flush()
    stored_response = complete_idempotency(claim, jsonable_encoder(item), status_code=201)
    db.commit()
    if stored_response:
        return stored_response.response()
    db.refresh(item)
    return item


@asset_router.get("/{asset_id}/download")
def download_asset(asset_id: str, membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    item = db.query(Asset).join(Episode, Asset.episode_id == Episode.id).filter(Asset.id == asset_id, Episode.organization_id == membership.organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Asset not found")
    if item.status == "deleted":
        raise HTTPException(status_code=410, detail="Asset has been deleted")
    if item.storage_provider == "local":
        if not item.local_path or not Path(item.local_path).is_file():
            raise HTTPException(status_code=404, detail="Asset file is missing")
        return FileResponse(item.local_path, media_type=item.mime_type, filename=item.original_filename)
    if not item.object_key:
        raise HTTPException(status_code=404, detail="Asset storage object is missing")
    try:
        storage = get_storage(item.storage_provider)
        url = storage.download_url(item.object_key)
    except StorageError as exc:
        raise HTTPException(status_code=502, detail="Unable to create a download URL") from exc
    if not url:
        raise HTTPException(status_code=502, detail="Storage provider does not support direct downloads")
    return {
        "asset_id": item.id,
        "storage_provider": item.storage_provider,
        "url": url,
        "expires_in": getattr(storage, "signed_url_expiry_seconds", None),
    }


@asset_router.patch("/{asset_id}")
def update_asset(asset_id: str, payload: AssetUpdate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.get(Asset, asset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Asset not found")
    values = payload.model_dump(exclude_unset=True)
    if "scene_id" in values and values["scene_id"]:
        scene = db.get(Scene, values["scene_id"])
        if not scene or scene.episode_id != item.episode_id:
            raise HTTPException(status_code=422, detail="Scene does not belong to this episode")
    if values.get("is_final"):
        db.query(Asset).filter(
            Asset.episode_id == item.episode_id,
            Asset.asset_type == item.asset_type,
            Asset.is_final.is_(True),
        ).update({Asset.is_final: False})
    for key, value in values.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@asset_router.delete("/{asset_id}")
def soft_delete_asset(asset_id: str, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.get(Asset, asset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Asset not found")
    item.status = "deleted"
    item.is_final = False
    db.commit()
    db.refresh(item)
    return {"status": "deleted", "id": item.id, "object_key": item.object_key}
