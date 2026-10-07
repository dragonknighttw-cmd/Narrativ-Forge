import json
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Asset, Episode, Subtitle
from ...services.storage import StorageError, materialize_asset
from ...services.subtitles import load_transcript, normalize_burmese_text, preset_config, render_srt, render_vtt, validate_cues
from ..dependencies import get_current_membership, get_current_user, require_roles

router = APIRouter(prefix="/episodes", tags=["subtitles"])
subtitle_router = APIRouter(prefix="/subtitles", tags=["subtitles"])

class Cue(BaseModel):
    start: float = Field(ge=0)
    end: float
    text: str = Field(min_length=1, max_length=500)

class SubtitleUpdate(BaseModel):
    cues: list[Cue] | None = None
    preset: str | None = None
    format: str | None = None
    status: str | None = None

class GenerateSubtitle(BaseModel):
    preset: str = "burmese_default"

def _episode_or_404(db: Session, episode_id: str, organization_id: str | None = None):
    episode = db.query(Episode).filter(Episode.id == episode_id, *( [Episode.organization_id == organization_id] if organization_id else [] )).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode


def _normalize_cues(cues):
    normalized = []
    for cue in cues:
        item = dict(cue)
        item["text"], _ = normalize_burmese_text(str(item.get("text") or "").strip())
        normalized.append(item)
    return normalized

def _serialize(item: Subtitle):
    return {
        "id": item.id, "episode_id": item.episode_id, "version": item.version,
        "language": item.language, "format": item.format, "preset": item.preset,
        "cues": json.loads(item.cues_json or "[]"), "status": item.status,
        "is_current": item.is_current,
        "validation_errors": json.loads(item.validation_errors_json or "[]"),
        "created_at": item.created_at, "updated_at": item.updated_at,
    }

@router.get("/{episode_id}/subtitles")
def list_subtitles(episode_id: str, limit: int = Query(default=50, ge=1, le=100), offset: int = Query(default=0, ge=0), membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id, membership.organization_id)
    query = db.query(Subtitle).filter(Subtitle.episode_id == episode_id).order_by(Subtitle.version.desc()).offset(offset).limit(limit)
    return [_serialize(x) for x in query.all()]

@router.post("/{episode_id}/subtitles/generate", status_code=201)
def generate_subtitle(episode_id: str, payload: GenerateSubtitle, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id, membership.organization_id)
    if payload.preset not in ("burmese_default", "burmese_compact"):
        raise HTTPException(status_code=422, detail="Unsupported subtitle preset")
    transcript = db.query(Asset).filter(
        Asset.episode_id == episode_id, Asset.asset_type == "transcript"
    ).order_by(Asset.version.desc()).first()
    if not transcript:
        raise HTTPException(status_code=422, detail="Transcript asset not found")
    try:
        with tempfile.TemporaryDirectory(prefix="nf-subtitle-") as work:
            transcript_path = materialize_asset(transcript, Path(work))
            cues = load_transcript(str(transcript_path))
    except StorageError as exc:
        raise HTTPException(status_code=422, detail="Transcript asset could not be read from storage") from exc
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        raise HTTPException(status_code=422, detail="Invalid transcript asset") from exc
    version = (db.query(func.max(Subtitle.version)).filter(Subtitle.episode_id == episode_id).scalar() or 0) + 1
    db.query(Subtitle).filter(Subtitle.episode_id == episode_id, Subtitle.is_current.is_(True)).update({Subtitle.is_current: False})
    errors = validate_cues(cues, payload.preset)
    item = Subtitle(episode_id=episode_id, version=version, preset=payload.preset, cues_json=json.dumps(cues, ensure_ascii=False), validation_errors_json=json.dumps(errors, ensure_ascii=False))
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)

@subtitle_router.post("/{subtitle_id}/versions", status_code=201)
def create_subtitle_version(subtitle_id: str, payload: SubtitleUpdate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    source = db.query(Subtitle).join(Episode, Subtitle.episode_id == Episode.id).filter(Subtitle.id == subtitle_id, Episode.organization_id == membership.organization_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    values = payload.model_dump(exclude_unset=True)
    cues = values.pop("cues", None)
    preset = values.get("preset", source.preset)
    if preset not in ("burmese_default", "burmese_compact"):
        raise HTTPException(status_code=422, detail="Unsupported subtitle preset")
    cue_data = cues if cues is not None else json.loads(source.cues_json or "[]")
    cue_data = _normalize_cues(cue_data)
    errors = validate_cues(cue_data, preset)
    version = (db.query(func.max(Subtitle.version)).filter(Subtitle.episode_id == source.episode_id).scalar() or 0) + 1
    db.query(Subtitle).filter(Subtitle.episode_id == source.episode_id, Subtitle.is_current.is_(True)).update({Subtitle.is_current: False})
    item = Subtitle(
        episode_id=source.episode_id,
        version=version,
        language=source.language,
        format=values.get("format", source.format),
        preset=preset,
        cues_json=json.dumps(cue_data, ensure_ascii=False),
        status="draft",
        is_current=True,
        validation_errors_json=json.dumps(errors, ensure_ascii=False),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)

@subtitle_router.patch("/{subtitle_id}")
def update_subtitle(subtitle_id: str, payload: SubtitleUpdate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.query(Subtitle).join(Episode, Subtitle.episode_id == Episode.id).filter(Subtitle.id == subtitle_id, Episode.organization_id == membership.organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    if item.status == "approved":
        raise HTTPException(status_code=409, detail="Approved subtitle is immutable; create a new version to edit")
    values = payload.model_dump(exclude_unset=True)
    cues = values.pop("cues", None)
    preset = values.get("preset", item.preset)
    if preset not in ("burmese_default", "burmese_compact"):
        raise HTTPException(status_code=422, detail="Unsupported subtitle preset")
    if cues is not None:
        cue_data = [cue if isinstance(cue, dict) else cue.model_dump() for cue in cues]
    else:
        cue_data = json.loads(item.cues_json or "[]")
    cue_data = _normalize_cues(cue_data)
    errors = validate_cues(cue_data, preset)
    item.cues_json = json.dumps(cue_data, ensure_ascii=False)
    item.validation_errors_json = json.dumps(errors, ensure_ascii=False)
    for key, value in values.items():
        setattr(item, key, value)
    item.status = "draft"
    db.commit()
    db.refresh(item)
    return _serialize(item)

@router.post("/{episode_id}/subtitles/import-cloud-transcript", status_code=201)
def import_cloud_transcript(
    episode_id: str,
    payload: dict,
    membership=Depends(get_current_membership),
    _: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    _episode_or_404(db, episode_id, membership.organization_id)
    vtt = str(payload.get("vtt") or "")
    preset = str(payload.get("preset") or "burmese_default")
    if preset not in ("burmese_default", "burmese_compact"):
        raise HTTPException(status_code=422, detail="Unsupported subtitle preset")
    if not vtt.strip():
        raise HTTPException(status_code=422, detail="Cloud transcript VTT is required")

    import re
    blocks = re.split(r"\n\s*\n", vtt.replace("\r\n", "\n").replace("\r", "\n"))
    cues = []
    timestamp = re.compile(r"(?P<start>\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2}\.\d{3})")
    def seconds(value: str) -> float:
        hours, minutes, rest = value.split(":")
        sec, millis = rest.split(".")
        return int(hours) * 3600 + int(minutes) * 60 + int(sec) + int(millis) / 1000

    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        match = next((timestamp.search(line) for line in lines), None)
        if not match:
            continue
        text_lines = lines[lines.index(next(line for line in lines if timestamp.search(line))) + 1:]
        text = " ".join(text_lines).strip()
        if not text:
            continue
        cues.append({
            "start": seconds(match.group("start")),
            "end": seconds(match.group("end")),
            "text": text,
        })
    if not cues:
        raise HTTPException(status_code=422, detail="No subtitle cues were found in Cloudflare VTT output")

    cues = _normalize_cues(cues)
    errors = validate_cues(cues, preset)
    version = (db.query(func.max(Subtitle.version)).filter(Subtitle.episode_id == episode_id).scalar() or 0) + 1
    db.query(Subtitle).filter(Subtitle.episode_id == episode_id, Subtitle.is_current.is_(True)).update({Subtitle.is_current: False})
    item = Subtitle(
        episode_id=episode_id,
        version=version,
        preset=preset,
        cues_json=json.dumps(cues, ensure_ascii=False),
        validation_errors_json=json.dumps(errors, ensure_ascii=False),
        status="draft",
        is_current=True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)


@router.post("/{episode_id}/subtitles/validate")
def validate_subtitles(episode_id: str, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    _episode_or_404(db, episode_id, membership.organization_id)
    item = db.query(Subtitle).filter(Subtitle.episode_id == episode_id, Subtitle.is_current.is_(True)).order_by(Subtitle.version.desc()).first()
    if not item:
        raise HTTPException(status_code=404, detail="Current subtitle not found")
    cues = json.loads(item.cues_json or "[]")
    errors = validate_cues(cues, item.preset)
    item.validation_errors_json = json.dumps(errors, ensure_ascii=False)
    db.commit()
    return {"valid": not errors, "errors": errors, "subtitle_id": item.id}

@router.post("/{episode_id}/subtitles/approve")
def approve_subtitles(episode_id: str, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    episode = _episode_or_404(db, episode_id, membership.organization_id)
    item = db.query(Subtitle).filter(Subtitle.episode_id == episode_id, Subtitle.is_current.is_(True)).order_by(Subtitle.version.desc()).first()
    if not item:
        raise HTTPException(status_code=404, detail="Current subtitle not found")
    errors = validate_cues(json.loads(item.cues_json or "[]"), item.preset)
    item.validation_errors_json = json.dumps(errors, ensure_ascii=False)
    if errors:
        db.commit()
        raise HTTPException(status_code=409, detail={"message": "Subtitle quality gate failed", "errors": errors})
    item.status = "approved"
    episode.status = "needs_approval"
    episode.current_step = "review"
    db.commit()
    db.refresh(item)
    return _serialize(item)

@subtitle_router.get("/{subtitle_id}/export")
def export_subtitle(subtitle_id: str, format: str = Query(default="srt"), membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    item = db.query(Subtitle).join(Episode, Subtitle.episode_id == Episode.id).filter(Subtitle.id == subtitle_id, Episode.organization_id == membership.organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Subtitle not found")
    if format not in ("srt", "vtt"):
        raise HTTPException(status_code=422, detail="Format must be srt or vtt")
    cues = json.loads(item.cues_json or "[]")
    content = render_srt(cues) if format == "srt" else render_vtt(cues)
    return PlainTextResponse(content, media_type="text/vtt" if format == "vtt" else "application/x-subrip")
