import json
from ...models import AuditEvent


def record_event(db, *, actor_email: str, action: str, resource_type: str, resource_id: str, metadata: dict | None = None) -> AuditEvent:
    event = AuditEvent(
        actor_email=actor_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True),
    )
    db.add(event)
    return event
