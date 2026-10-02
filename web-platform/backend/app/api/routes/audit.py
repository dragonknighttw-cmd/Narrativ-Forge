from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import AuditEvent
from ..dependencies import require_roles

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
def list_audit_events(
    limit: int = Query(default=50, ge=1, le=100),
    user=Depends(require_roles("owner")),
    db: Session = Depends(get_db),
):
    events = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit).all()
    return [{
        "id": event.id,
        "actor_email": event.actor_email,
        "action": event.action,
        "resource_type": event.resource_type,
        "resource_id": event.resource_id,
        "metadata": event.metadata_json,
        "created_at": event.created_at,
    } for event in events]
