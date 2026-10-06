import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...db import get_db
from ...models import Episode, HookLibrary, ManualProductionLog, SocialAnalyticsRecord, SocialPublication
from ..dependencies import get_current_membership, get_current_user, require_roles

router = APIRouter(tags=["production-intelligence"])

HOOK_TYPES = {"question", "shock", "mystery", "warning", "personal_story", "contrarian", "cliffhanger", "number"}
PUBLICATION_STATES = {"not_ready", "prepared", "scheduled_metadata_ready", "manually_published", "published_recorded"}

PLATFORMS = {"youtube_shorts", "tiktok", "instagram_reels", "facebook_reels"}
MAX_HASHTAGS = 30

def validate_publication_payload(platform: str, caption: str, hashtags: list[str]) -> list[str]:
    errors = []
    if platform not in PLATFORMS:
        errors.append("Unsupported platform")
    if not caption.strip():
        errors.append("Caption is required")
    if len(caption) > 2200:
        errors.append("Caption exceeds 2200 characters")
    if len(hashtags) > MAX_HASHTAGS:
        errors.append("Too many hashtags")
    if any(not tag.strip() or len(tag.strip()) > 100 for tag in hashtags):
        errors.append("Hashtags must be non-empty and <= 100 characters")
    return errors



def serialize_hook(item: HookLibrary):
    return {
        "id": item.id, "hook_text": item.hook_text, "hook_type": item.hook_type,
        "topic": item.topic, "emotion": item.emotion, "used_count": item.used_count,
        "views_average": item.views_average, "completion_average": item.completion_average,
        "shares_average": item.shares_average, "performance_score": item.performance_score,
        "is_default": item.is_default, "created_at": item.created_at, "updated_at": item.updated_at,
    }


class HookCreate(BaseModel):
    hook_text: str = Field(min_length=1)
    hook_type: str
    topic: str | None = None
    emotion: str | None = None
    used_count: int = Field(default=0, ge=0)
    views_average: float | None = Field(default=None, ge=0)
    completion_average: float | None = Field(default=None, ge=0)
    shares_average: float | None = Field(default=None, ge=0)
    performance_score: float | None = Field(default=None, ge=0)
    is_default: bool = False


class HookUpdate(HookCreate):
    pass


@router.get("/hooks")
def list_hooks(_: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return [serialize_hook(x) for x in db.query(HookLibrary).order_by(HookLibrary.created_at.desc()).all()]


@router.post("/hooks", status_code=201)
def create_hook(payload: HookCreate, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    if payload.hook_type not in HOOK_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported hook type")
    if payload.is_default:
        db.query(HookLibrary).update({HookLibrary.is_default: False})
    item = HookLibrary(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_hook(item)


@router.patch("/hooks/{hook_id}")
def update_hook(hook_id: str, payload: HookUpdate, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.get(HookLibrary, hook_id)
    if not item:
        raise HTTPException(status_code=404, detail="Hook not found")
    if payload.hook_type not in HOOK_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported hook type")
    if payload.is_default:
        db.query(HookLibrary).filter(HookLibrary.id != hook_id).update({HookLibrary.is_default: False})
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return serialize_hook(item)


@router.get("/hooks/recommendations")
def recommend_hooks(membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    """Return evidence-backed hook recommendations after enough production data exists."""
    logs = (
        db.query(ManualProductionLog)
        .join(Episode, ManualProductionLog.episode_id == Episode.id)
        .filter(
            Episode.organization_id == membership.organization_id,
            ManualProductionLog.published.is_(True),
        )
        .all()
    )
    if len(logs) < 5:
        return {
            "ready": False,
            "minimum_samples": 5,
            "sample_count": len(logs),
            "recommendations": [],
        }

    rows = (
        db.query(
            HookLibrary,
            func.count(ManualProductionLog.id),
            func.coalesce(func.avg(ManualProductionLog.completion_rate), 0),
            func.coalesce(func.avg(ManualProductionLog.views), 0),
            func.coalesce(func.avg(ManualProductionLog.shares), 0),
        )
        .join(ManualProductionLog, ManualProductionLog.hook_type == HookLibrary.hook_type)
        .join(Episode, ManualProductionLog.episode_id == Episode.id)
        .filter(
            Episode.organization_id == membership.organization_id,
            ManualProductionLog.published.is_(True),
        )
        .group_by(HookLibrary.id)
        .having(func.count(ManualProductionLog.id) >= 2)
        .all()
    )

    recommendations = []
    for hook, sample_count, completion_avg, views_avg, shares_avg in rows:
        score = (
            float(completion_avg) * 0.5
            + min(float(views_avg) / 10000.0, 1.0) * 0.3
            + min(float(shares_avg) / 100.0, 1.0) * 0.2
        )
        recommendations.append({
            **serialize_hook(hook),
            "evidence_sample_count": sample_count,
            "evidence_score": round(score, 4),
            "evidence_completion_average": round(float(completion_avg), 4),
            "evidence_views_average": round(float(views_avg), 2),
            "evidence_shares_average": round(float(shares_avg), 2),
        })

    recommendations.sort(key=lambda item: item["evidence_score"], reverse=True)
    return {
        "ready": True,
        "minimum_samples": 5,
        "sample_count": len(logs),
        "recommendations": recommendations[:10],
    }


def serialize_log(item: ManualProductionLog):
    return {column.name: getattr(item, column.name) for column in ManualProductionLog.__table__.columns}


class ProductionLogCreate(BaseModel):
    episode_id: str | None = None
    topic: str
    category: str | None = None
    hook: str | None = None
    hook_type: str | None = None
    script_length: int | None = Field(default=None, ge=0)
    duration_seconds: int | None = Field(default=None, ge=0)
    scene_count: int | None = Field(default=None, ge=0)
    voice_tool: str | None = None
    image_tool: str | None = None
    video_tool: str | None = None
    subtitle_style: str | None = None
    production_time_seconds: int | None = Field(default=None, ge=0)
    manual_errors: str | None = None
    quality_score: float | None = Field(default=None, ge=0)
    published: bool = False
    platform: str | None = None
    views: int | None = Field(default=None, ge=0)
    watch_time_seconds: int | None = Field(default=None, ge=0)
    completion_rate: float | None = Field(default=None, ge=0)
    shares: int | None = Field(default=None, ge=0)
    saves: int | None = Field(default=None, ge=0)
    notes: str | None = None



@router.delete("/hooks/{hook_id}", status_code=204)
def delete_hook(hook_id: str, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.get(HookLibrary, hook_id)
    if not item:
        raise HTTPException(status_code=404, detail="Hook not found")
    if item.is_default:
        raise HTTPException(status_code=409, detail="Default hook cannot be deleted")
    db.delete(item)
    db.commit()
    return None


@router.get("/manual-production-logs")
def list_production_logs(membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    rows = (db.query(ManualProductionLog).outerjoin(Episode, ManualProductionLog.episode_id == Episode.id)
        .filter((ManualProductionLog.episode_id.is_(None)) | (Episode.organization_id == membership.organization_id))
        .order_by(ManualProductionLog.created_at.desc()).all())
    return [serialize_log(x) for x in rows]



class ProductionLogUpdate(BaseModel):
    episode_id: str | None = None
    topic: str | None = None
    category: str | None = None
    hook: str | None = None
    hook_type: str | None = None
    script_length: int | None = Field(default=None, ge=0)
    duration_seconds: int | None = Field(default=None, ge=0)
    scene_count: int | None = Field(default=None, ge=0)
    voice_tool: str | None = None
    image_tool: str | None = None
    video_tool: str | None = None
    subtitle_style: str | None = None
    production_time_seconds: int | None = Field(default=None, ge=0)
    manual_errors: str | None = None
    quality_score: float | None = Field(default=None, ge=0)
    published: bool | None = None
    platform: str | None = None
    views: int | None = Field(default=None, ge=0)
    watch_time_seconds: int | None = Field(default=None, ge=0)
    completion_rate: float | None = Field(default=None, ge=0)
    shares: int | None = Field(default=None, ge=0)
    saves: int | None = Field(default=None, ge=0)
    notes: str | None = None


@router.patch("/manual-production-logs/{log_id}")
def update_production_log(log_id: str, payload: ProductionLogUpdate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = (db.query(ManualProductionLog).outerjoin(Episode, ManualProductionLog.episode_id == Episode.id).filter(ManualProductionLog.id == log_id, (ManualProductionLog.episode_id.is_(None)) | (Episode.organization_id == membership.organization_id)).first())
    if not item:
        raise HTTPException(status_code=404, detail="Production log not found")
    if payload.episode_id and not db.query(Episode).filter(Episode.id == payload.episode_id, Episode.organization_id == membership.organization_id).first():
        raise HTTPException(status_code=404, detail="Episode not found")
    if payload.hook_type and payload.hook_type not in HOOK_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported hook type")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return serialize_log(item)


@router.delete("/manual-production-logs/{log_id}", status_code=204)
def delete_production_log(log_id: str, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.get(ManualProductionLog, log_id)
    if not item:
        raise HTTPException(status_code=404, detail="Production log not found")
    db.delete(item)
    db.commit()
    return None


@router.post("/manual-production-logs", status_code=201)
def create_production_log(payload: ProductionLogCreate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    if payload.episode_id and not db.query(Episode).filter(Episode.id == payload.episode_id, Episode.organization_id == membership.organization_id).first():
        raise HTTPException(status_code=404, detail="Episode not found")
    if payload.hook_type and payload.hook_type not in HOOK_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported hook type")
    item = ManualProductionLog(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_log(item)


def serialize_publication(item: SocialPublication):
    return {
        "id": item.id, "episode_id": item.episode_id, "platform": item.platform,
        "state": item.state, "caption": item.caption, "hashtags": json.loads(item.hashtags_json or "[]"),
        "schedule_metadata": json.loads(item.schedule_metadata_json or "{}"),
        "platform_format_valid": item.platform_format_valid, "publish_url": item.publish_url,
        "published_at": item.published_at, "notes": item.notes, "created_at": item.created_at, "updated_at": item.updated_at,
    }


class PublicationCreate(BaseModel):
    episode_id: str
    platform: str
    caption: str = ""
    hashtags: list[str] = Field(default_factory=list)
    schedule_metadata: dict = Field(default_factory=dict)
    platform_format_valid: bool = False
    notes: str | None = None


class PublicationUpdate(PublicationCreate):
    state: str = "not_ready"
    publish_url: str | None = None
    published_at: datetime | None = None


@router.get("/episodes/{episode_id}/social-prep")
def list_social_prep(episode_id: str, membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    if not db.query(Episode).filter(Episode.id == episode_id, Episode.organization_id == membership.organization_id).first():
        raise HTTPException(status_code=404, detail="Episode not found")
    return [serialize_publication(x) for x in db.query(SocialPublication).filter(SocialPublication.episode_id == episode_id).order_by(SocialPublication.created_at.desc()).all()]


@router.post("/social-prep", status_code=201)
def create_social_prep(payload: PublicationCreate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    if not db.query(Episode).filter(Episode.id == payload.episode_id, Episode.organization_id == membership.organization_id).first():
        raise HTTPException(status_code=404, detail="Episode not found")
    errors = validate_publication_payload(payload.platform, payload.caption, payload.hashtags)
    if errors:
        raise HTTPException(status_code=422, detail={"message": "Publishing preparation validation failed", "errors": errors})
    item = SocialPublication(
        episode_id=payload.episode_id, platform=payload.platform, caption=payload.caption,
        hashtags_json=json.dumps(payload.hashtags, ensure_ascii=False),
        schedule_metadata_json=json.dumps(payload.schedule_metadata, ensure_ascii=False),
        platform_format_valid=payload.platform_format_valid, notes=payload.notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_publication(item)


@router.patch("/social-prep/{publication_id}")
def update_social_prep(publication_id: str, payload: PublicationUpdate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.query(SocialPublication).join(Episode, SocialPublication.episode_id == Episode.id).filter(SocialPublication.id == publication_id, Episode.organization_id == membership.organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Social preparation not found")
    if payload.state not in PUBLICATION_STATES:
        raise HTTPException(status_code=422, detail="Invalid publishing state")
    errors = validate_publication_payload(payload.platform, payload.caption, payload.hashtags)
    if errors:
        raise HTTPException(status_code=422, detail={"message": "Publishing preparation validation failed", "errors": errors})
    if payload.state in {"manually_published", "published_recorded"} and not payload.publish_url:
        raise HTTPException(status_code=409, detail="Publish URL is required for a published record")
    item.platform = payload.platform
    item.caption = payload.caption
    item.hashtags_json = json.dumps(payload.hashtags, ensure_ascii=False)
    item.schedule_metadata_json = json.dumps(payload.schedule_metadata, ensure_ascii=False)
    item.platform_format_valid = payload.platform_format_valid
    item.notes = payload.notes
    item.state = payload.state
    item.publish_url = payload.publish_url
    item.published_at = payload.published_at
    db.commit()
    db.refresh(item)
    return serialize_publication(item)


class AnalyticsCreate(BaseModel):
    views: int = Field(default=0, ge=0)
    watch_time_seconds: int = Field(default=0, ge=0)
    completion_rate: float = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    source: str = "manual"


@router.get("/social-prep/{publication_id}/analytics")
def list_analytics(publication_id: str, membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    if not db.query(SocialPublication).join(Episode, SocialPublication.episode_id == Episode.id).filter(SocialPublication.id == publication_id, Episode.organization_id == membership.organization_id).first():
        raise HTTPException(status_code=404, detail="Social preparation not found")
    return db.query(SocialAnalyticsRecord).filter(SocialAnalyticsRecord.publication_id == publication_id).order_by(SocialAnalyticsRecord.recorded_at.desc()).all()


@router.post("/social-prep/{publication_id}/analytics", status_code=201)
def create_analytics(publication_id: str, payload: AnalyticsCreate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    publication = db.query(SocialPublication).join(Episode, SocialPublication.episode_id == Episode.id).filter(SocialPublication.id == publication_id, Episode.organization_id == membership.organization_id).first()
    if not publication:
        raise HTTPException(status_code=404, detail="Social preparation not found")
    item = SocialAnalyticsRecord(publication_id=publication_id, **payload.model_dump())
    db.add(item)
    if publication.state == "manually_published":
        publication.state = "published_recorded"
    db.commit()
    db.refresh(item)
    return item


@router.get("/analytics")
def analytics_summary(membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    logs = db.query(ManualProductionLog).outerjoin(Episode, ManualProductionLog.episode_id == Episode.id).filter((ManualProductionLog.episode_id.is_(None)) | (Episode.organization_id == membership.organization_id)).all()
    analytics = db.query(SocialAnalyticsRecord).join(SocialPublication).join(Episode).filter(Episode.organization_id == membership.organization_id).all()
    platform_rows = (
        db.query(
            SocialPublication.platform,
            func.count(SocialAnalyticsRecord.id),
            func.coalesce(func.sum(SocialAnalyticsRecord.views), 0),
            func.coalesce(func.sum(SocialAnalyticsRecord.shares), 0),
            func.coalesce(func.sum(SocialAnalyticsRecord.saves), 0),
        )
        .join(Episode, SocialPublication.episode_id == Episode.id)
        .join(SocialAnalyticsRecord, SocialAnalyticsRecord.publication_id == SocialPublication.id)
        .filter(Episode.organization_id == membership.organization_id)
        .group_by(SocialPublication.platform)
        .all()
    )
    hook_rows = (
        db.query(
            ManualProductionLog.hook_type,
            func.count(ManualProductionLog.id),
            func.coalesce(func.sum(ManualProductionLog.views), 0),
        )
        .join(Episode, ManualProductionLog.episode_id == Episode.id).filter(ManualProductionLog.hook_type.isnot(None), Episode.organization_id == membership.organization_id)
        .group_by(ManualProductionLog.hook_type)
        .all()
    )
    return {
        "manual_logs": len(logs),
        "published_logs": sum(1 for x in logs if x.published),
        "social_records": len(analytics),
        "views": sum(x.views for x in analytics),
        "watch_time_seconds": sum(x.watch_time_seconds for x in analytics),
        "shares": sum(x.shares for x in analytics),
        "saves": sum(x.saves for x in analytics),
        "comments": sum(x.comments for x in analytics),
        "average_completion_rate": (sum(x.completion_rate for x in analytics) / len(analytics)) if analytics else 0,
        "by_platform": [
            {"platform": row[0], "records": row[1], "views": row[2], "shares": row[3], "saves": row[4]}
            for row in platform_rows
        ],
        "by_hook_type": [
            {"hook_type": row[0], "logs": row[1], "views": row[2]}
            for row in hook_rows
        ],
    }
