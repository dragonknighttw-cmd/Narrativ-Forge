from pathlib import Path
import re
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import get_db
from ...models import Asset, Episode, Scene
from ..dependencies import get_current_user

router = APIRouter(prefix="/episodes", tags=["assets"])

ALLOWED_TYPES = {
    "video": {"video/mp4", "video/webm", "video/quicktime"},
    "audio": {"audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4"},
    "image": {"image/jpeg", "image/png", "image/webp"},
    "thumbnail": {"image/jpeg", "image/png", "image/webp"},
}
MAX_FILE_SIZE = settings.max_upload_size_bytes
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
    _: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _episode_or_404(db, episode_id)
    validate_upload(file.filename or "", file.content_type, asset_type)
    if scene_id:
        scene = db.get(Scene, scene_id)
        if not scene or scene.episode_id != episode_id:
            raise HTTPException(status_code=422, detail="Scene does not belong to this episode")
    upload_dir = Path(settings.upload_dir) / episode_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    version = (db.query(func.max(Asset.version)).filter(Asset.episode_id == episode_id).scalar() or 0) + 1
    safe_name = safe_filename(file.filename or "upload.bin")
    stored_name = f"{uuid4().hex}_v{version}_{safe_name}"
    destination = upload_dir / stored_name
    size = 0
    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_upload_size_bytes:
                    destination.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="File exceeds upload size limit")
                output.write(chunk)
    except HTTPException:
        raise
    except OSError as exc:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Unable to store upload") from exc
    item = Asset(
        episode_id=episode_id,
        scene_id=scene_id,
        asset_type=asset_type,
        original_filename=safe_name,
        storage_provider="local",
        local_path=str(destination),
        mime_type=file.content_type or "application/octet-stream",
        file_size_bytes=size,
        version=version,
        copyright_status=copyright_status,
        status="uploaded",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/../assets/{asset_id}")
def update_asset(asset_id: str, payload: AssetUpdate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Asset, asset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Asset not found")
    values = payload.model_dump(exclude_unset=True)
    if "scene_id" in values and values["scene_id"]:
        scene = db.get(Scene, values["scene_id"])
        if not scene or scene.episode_id != item.episode_id:
            raise HTTPException(status_code=422, detail="Scene does not belong to this episode")
    if values.get("is_final"):
        db.query(Asset).filter(Asset.episode_id == item.episode_id, Asset.asset_type == item.asset_type, Asset.is_final.is_(True)).update({Asset.is_final: False})
    for key, value in values.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item
