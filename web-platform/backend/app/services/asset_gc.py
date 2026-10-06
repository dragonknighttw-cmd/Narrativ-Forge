from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from ..models.core import UploadSession
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.core import Asset, AuditEvent
from .storage import StorageError, get_storage

logger = logging.getLogger(__name__)


def purge_deleted_assets(db: Session, *, now: datetime | None = None, limit: int = 100) -> int:
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=settings.asset_retention_days)
    assets = list(
        db.scalars(
            select(Asset)
            .where(Asset.status == "deleted", Asset.deleted_at.is_not(None), Asset.deleted_at < cutoff)
            .order_by(Asset.deleted_at.asc())
            .limit(limit)
        )
    )
    purged = 0
    for asset in assets:
        try:
            if asset.object_key:
                get_storage(asset.storage_provider).delete(asset.object_key)
        except StorageError:
            logger.exception("asset_gc_storage_delete_failed", extra={"asset_id": asset.id})
            continue
        db.add(AuditEvent(
            actor_email="system",
            action="asset.purged",
            resource_type="asset",
            resource_id=asset.id,
            metadata_json='{"reason":"retention"}',
        ))
        db.delete(asset)
        purged += 1
    if purged:
        db.commit()
    return purged


def purge_stale_local_multipart_uploads(
    db: Session,
    *,
    now: datetime | None = None,
    limit: int = 100,
) -> int:
    """Remove expired local multipart staging directories that are no longer active in DB."""
    now = now or datetime.now(timezone.utc)
    root = (settings.upload_dir and __import__("pathlib").Path(settings.upload_dir) / ".multipart")
    if not root or not root.exists():
        return 0

    active_ids = {
        row[0]
        for row in db.execute(
            select(UploadSession.provider_upload_id).where(
                UploadSession.status == "active",
                UploadSession.expires_at > now,
                UploadSession.provider_upload_id.is_not(None),
            )
        ).all()
    }
    removed = 0
    for directory in sorted(root.iterdir(), key=lambda item: item.stat().st_mtime if item.exists() else 0):
        if removed >= limit or not directory.is_dir():
            continue
        if directory.name in active_ids:
            continue
        metadata = directory / "metadata.json"
        try:
            modified_at = datetime.fromtimestamp(directory.stat().st_mtime, timezone.utc)
            if modified_at > now - timedelta(hours=settings.temp_file_retention_hours):
                continue
            import shutil
            shutil.rmtree(directory)
            removed += 1
        except OSError:
            logger.exception("multipart_gc_cleanup_failed", extra={"path": str(directory)})
    return removed
