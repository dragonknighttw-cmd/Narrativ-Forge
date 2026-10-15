import json
from sqlalchemy import select
from ..models import AuditEvent, Idea, Series, Episode, ProcessingJob, Asset, Script, Subtitle, Scene, ExportRecord, ReviewRecord, ManualProductionLog, SocialPublication

def _infer_org(db, resource_type: str, resource_id: str) -> str | None:
    direct = {
        "idea": Idea,
        "series": Series,
        "episode": Episode,
    }
    model = direct.get(resource_type)
    if model is not None:
        row = db.query(model.organization_id).filter(model.id == resource_id).first()
        return row[0] if row else None
    episode_models = {
        "processing_job": ProcessingJob,
        "asset": Asset,
        "script": Script,
        "subtitle": Subtitle,
        "scene": Scene,
        "export": ExportRecord,
        "review": ReviewRecord,
        "production_log": ManualProductionLog,
        "social_publication": SocialPublication,
    }
    model = episode_models.get(resource_type)
    if model is None:
        return None
    row = db.query(Episode.organization_id).join(model, model.episode_id == Episode.id).filter(model.id == resource_id).first()
    return row[0] if row else None

def record_event(db, *, actor_email: str, action: str, resource_type: str, resource_id: str, metadata: dict | None = None, organization_id: str | None = None) -> AuditEvent:
    resolved_org = organization_id or _infer_org(db, resource_type, resource_id)
    event = AuditEvent(
        organization_id=resolved_org,
        actor_email=actor_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True),
    )
    db.add(event)
    return event
