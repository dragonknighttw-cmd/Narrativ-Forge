from pathlib import Path
import re
import tempfile
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import get_db
from ...models import Asset, Episode, Scene
from ...services.storage import StorageError, build_object_key, get_storage
from ..dependencies import get_current_user, require_roles

router = APIRouter(prefix="/episodes", tags=["assets"])
asset_router = APIRouter(prefix="/assets", tags=["assets"])

ALLOWED_TYPES = {
    "video": {"video/mp4", "video/webm", "video/quicktime"},
    "audio": {"audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4"},
    "image": {"image/jpeg", "image/png", "image/webp"},
    "thumbnail": {"image/jpeg", "image/png", "image/webp"},
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
        "video": {".mp4", ".webm", ".mov"},
        "audio": {".mp3", ".wav", ".m4a"},
    }
    if suffix not in suffixes[asset_type]:
        raise HTTPException(status_code=415, detail="Unsupported file extension")


def _episode_or_404(db: Session, episode_id: str) -> Episode:
    item = db.get(Episode, episode_id)
    if not item:
        raise HTTPException(status_code=404, detail="Episode not found")
    return item


@router.get("/{episode_id}/assets")
def list_assets(episode_id: str, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id)
    return db.query(Asset).filter(Asset.episode_id == episode_id).order_by(Asset.created_at.desc()).all()


@router.post("/{episode_id}/assets/upload", status_code=201)
async def upload_asset(
    episode_id: str,
    file: UploadFile = File(...),
    asset_type: str = Form(...),
    scene_id: str | None = Form(default=None),
    copyright_status: str = Form(default="unknown"),
    _: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    _episode_or_404(db, episode_id)
    validate_upload(file.filename or "", file.content_type, asset_type)
    if scene_id:
        scene = db.get(Scene, scene_id)
        if not scene or scene.episode_id != episode_id:
            raise HTTPException(status_code=422, detail="Scene does not belong to this episode")

    version = (db.query(func.max(Asset.version)).filter(Asset.episode_id == episode_id).scalar() or 0) + 1
    safe_name = safe_filename(file.filename or "upload.bin")
    object_key = build_object_key(episode_id, version, f"{uuid4().hex}_{safe_name}", asset_type)

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix="nf-upload-", suffix=Path(safe_name).suffix, delete=False) as temp:
            temp_path = Path(temp.name)
            size = 0
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_upload_size_bytes:
                    raise HTTPException(status_code=413, detail="File exceeds upload size limit")
                temp.write(chunk)

        stored = get_storage().upload_file(temp_path, object_key, file.content_type or "application/octet-stream")
    except HTTPException:
        raise
    except StorageError as exc:
        raise HTTPException(status_code=502, detail="Unable to store upload") from exc
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)

    item = Asset(
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
    db.commit()
    db.refresh(item)
    return item


@asset_router.get("/{asset_id}/download")
def download_asset(asset_id: str, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Asset, asset_id)
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
        url = get_storage(item.storage_provider).download_url(item.object_key)
    except StorageError as exc:
        raise HTTPException(status_code=502, detail="Unable to create a download URL") from exc
    if not url:
        raise HTTPException(status_code=502, detail="Storage provider does not support direct downloads")
    return {"asset_id": item.id, "storage_provider": item.storage_provider, "url": url, "expires_in": settings.b2_signed_url_expiry_seconds}


@asset_router.patch("/{asset_id}")
def update_asset(asset_id: str, payload: AssetUpdate, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
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
def soft_delete_asset(asset_id: str, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.get(Asset, asset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Asset not found")
    item.status = "deleted"
    item.is_final = False
    db.commit()
    db.refresh(item)
    return {"status": "deleted", "id": item.id, "object_key": item.object_key}
