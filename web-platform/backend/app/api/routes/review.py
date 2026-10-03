import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, selectinload

from ...db import get_db
from ...models import Asset, Episode, ReviewRecord, Subtitle
from ...services.audit import record_event
from ..dependencies import get_current_user, require_roles

router = APIRouter(prefix="/episodes", tags=["review"])

CRITICAL_TYPES = {"missing_video", "missing_audio", "missing_thumbnail", "subtitle_timing", "copyright"}
CHECK_KEYS = ("video_watched", "audio_checked", "subtitle_timing_checked", "thumbnail_present")

class ReviewUpdate(BaseModel):
    video_watched: bool = False
    audio_checked: bool = False
    subtitle_timing_checked: bool = False
    thumbnail_present: bool = False
    critical_issues: list[str] = Field(default_factory=list)
    notes: str = ""

class RevisionRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)

def _episode(db, episode_id, *, load_review_data=False):
    query = db.query(Episode)
    if load_review_data:
        query = query.options(
            selectinload(Episode.assets),
            selectinload(Episode.subtitles),
        )
    item = query.filter(Episode.id == episode_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Episode not found")
    return item

def _review_assets(episode: Episode):
    video = any(a.asset_type in {"processed_video", "video"} and a.is_final for a in episode.assets)
    thumbnail = any(a.asset_type == "thumbnail" for a in episode.assets)
    return {"video_watched": video, "thumbnail_present": thumbnail}

def _current_episode_subtitle(episode: Episode):
    return max(
        (subtitle for subtitle in episode.subtitles if subtitle.is_current),
        key=lambda subtitle: subtitle.version,
        default=None,
    )

def _current_subtitle(db, episode_id):
    return db.query(Subtitle).filter(Subtitle.episode_id == episode_id, Subtitle.is_current.is_(True)).order_by(Subtitle.version.desc()).first()

@router.get("/{episode_id}/review")
def get_review(episode_id: str, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    episode = _episode(db, episode_id, load_review_data=True)
    subtitle = _current_episode_subtitle(episode)
    assets = _review_assets(episode)
    return {
        "episode_id": episode.id,
        "status": episode.status,
        "checklist": {
            "video_watched": assets["video_watched"],
            "audio_checked": False,
            "subtitle_timing_checked": bool(subtitle and not json.loads(subtitle.validation_errors_json or "[]")),
            "thumbnail_present": assets["thumbnail_present"],
        },
        "critical_issues": [],
        "notes": "",
        "blocking_reasons": [] if subtitle and not json.loads(subtitle.validation_errors_json or "[]") else ["Subtitle validation must pass."],
    }

@router.post("/{episode_id}/review")
def save_review(episode_id: str, payload: ReviewUpdate, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    episode = _episode(db, episode_id)
    if episode.status not in {"subtitle_review", "needs_approval", "rejected"}:
        raise HTTPException(status_code=409, detail="Episode is not in review workflow")
    subtitle = _current_subtitle(db, episode_id)
    blockers = []
    if not payload.video_watched: blockers.append("Video must be watched.")
    if not payload.audio_checked: blockers.append("Audio must be checked.")
    if not payload.subtitle_timing_checked: blockers.append("Subtitle timing must be checked.")
    if not payload.thumbnail_present: blockers.append("Thumbnail is required.")
    if payload.critical_issues: blockers.append("Critical issues must be resolved.")
    if not subtitle or json.loads(subtitle.validation_errors_json or "[]"): blockers.append("Subtitle validation must pass.")
    record = db.query(ReviewRecord).filter(ReviewRecord.episode_id == episode_id).first()
    if not record:
        record = ReviewRecord(episode_id=episode_id)
        db.add(record)
    record.checklist_json = json.dumps({key: getattr(payload, key) for key in CHECK_KEYS})
    record.critical_issues_json = json.dumps(payload.critical_issues, ensure_ascii=False)
    record.notes = payload.notes
    record.decision = "pending" if blockers else "ready"
    record.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"saved": True, "blocking_reasons": blockers, "ready": not blockers, "review": payload.model_dump()}

@router.post("/{episode_id}/review/request-revision")
def request_revision(episode_id: str, payload: RevisionRequest, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    episode = _episode(db, episode_id)
    if episode.status not in {"subtitle_review", "needs_approval", "rejected"}:
        raise HTTPException(status_code=409, detail="Episode is not in review workflow")
    record = db.query(ReviewRecord).filter(ReviewRecord.episode_id == episode_id).first()
    if record:
        record.decision = "revision_requested"
        record.revision_reason = payload.reason
        record.reviewed_at = datetime.now(timezone.utc)
    episode.status = "in_production"
    episode.current_step = "production"
    db.commit()
    return {"status": "rejected", "reason": payload.reason, "episode_id": episode.id}

@router.post("/{episode_id}/review/approve")
def approve_review(episode_id: str, payload: ReviewUpdate, user=Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    episode = _episode(db, episode_id)
    if episode.status != "needs_approval":
        raise HTTPException(status_code=409, detail="Episode must be in needs_approval before final approval")
    blockers = []
    if not all(payload.model_dump().get(k, False) for k in CHECK_KEYS): blockers.append("All approval checklist items are required.")
    if payload.critical_issues: blockers.append("Critical issues must be resolved.")
    subtitle = _current_subtitle(db, episode_id)
    if not subtitle or subtitle.status != "approved": blockers.append("Approved subtitle is required.")
    if blockers: raise HTTPException(status_code=409, detail={"message": "Approval blocked", "blocking_reasons": blockers})
    record = db.query(ReviewRecord).filter(ReviewRecord.episode_id == episode_id).first()
    if not record:
        record = ReviewRecord(episode_id=episode_id)
        db.add(record)
    record.checklist_json = json.dumps({key: getattr(payload, key) for key in CHECK_KEYS})
    record.critical_issues_json = json.dumps(payload.critical_issues, ensure_ascii=False)
    record.notes = payload.notes
    record.decision = "approved"
    record.reviewed_at = datetime.now(timezone.utc)
    episode.status = "approved"
    episode.current_step = "review"
    final_asset = db.query(Asset).filter(Asset.episode_id == episode_id, Asset.asset_type == "processed_video").order_by(Asset.version.desc()).first()
    if final_asset:
        final_asset.is_final = True
        final_asset.status = "final"
    approved_at = datetime.now(timezone.utc)
    record_event(db, actor_email=user["email"], action="episode.approved", resource_type="episode", resource_id=episode.id, metadata={"review_id": record.id, "final_asset_id": final_asset.id if final_asset else None})
    db.commit()
    return {"approved": True, "episode_id": episode.id, "status": episode.status, "approved_at": approved_at.isoformat()}
