from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
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
