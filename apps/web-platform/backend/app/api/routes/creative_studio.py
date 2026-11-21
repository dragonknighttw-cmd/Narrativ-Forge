from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models.creative_studio import (
    CreativeDirectorConcept,
    MusicScoreAsset,
    QualityControlReport,
    RawFootage,
    ReferenceVideo,
    SoundDesignAsset,
    TimelineProject,
)
from ...services.creative_studio import CreativeStudioService
from ..dependencies import get_current_membership, require_roles

router = APIRouter(
    prefix="/creative-studio",
    tags=["creative-studio-expansion"],
    dependencies=[Depends(get_current_membership)],
)


# ==========================================
# Pydantic Schemas
# ==========================================

class ReferenceAnalyzeRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    file_url: str = Field(min_length=1)
    duration_seconds: float = Field(default=60.0, gt=0.0)
    user_notes: Optional[str] = None


class FootageScanRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    file_url: str = Field(min_length=1)
    duration_seconds: float = Field(default=30.0, gt=0.0)
    resolution: str = Field(default="1080x1920")


class GenerateConceptsRequest(BaseModel):
    episode_title: str = Field(min_length=1, max_length=255)
    logline: str = Field(min_length=1)
    target_duration_seconds: int = Field(default=180, ge=15, le=900)


class TimelineSaveRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    target_aspect_ratio: str = Field(default="9:16")
    tracks: Dict[str, Any] = Field(default_factory=dict)
    duration_seconds: float = Field(default=0.0, ge=0.0)


# ==========================================
# Helpers
# ==========================================

def _get_org_id(membership: Any) -> Optional[str]:
    if isinstance(membership, dict):
        return membership.get("organization_id")
    return getattr(membership, "organization_id", None)


# ==========================================
# Overview Stats
# ==========================================

@router.get("/overview")
def get_studio_overview(
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    """Summary metrics of the AI Creative Production Studio."""
    org_id = _get_org_id(membership)
    ref_q = db.query(ReferenceVideo)
    footage_q = db.query(RawFootage)
    concept_q = db.query(CreativeDirectorConcept)
    timeline_q = db.query(TimelineProject)

    if org_id:
        ref_q = ref_q.filter(ReferenceVideo.organization_id == org_id)
        footage_q = footage_q.filter(RawFootage.organization_id == org_id)
        concept_q = concept_q.filter(CreativeDirectorConcept.organization_id == org_id)
        timeline_q = timeline_q.filter(TimelineProject.organization_id == org_id)

    ref_count = ref_q.count()
    footage_count = footage_q.count()
    concept_count = concept_q.count()
    timeline_count = timeline_q.count()

    return {
        "status": "online",
        "studio_edition": "AI Creative Production Studio v2.0",
        "counts": {
            "reference_videos": ref_count,
            "raw_footages": footage_count,
            "creative_concepts": concept_count,
            "timeline_projects": timeline_count,
            "curated_music_tracks": 4,
            "curated_sfx_tracks": 4,
        },
        "active_capabilities": [
            "Reference Video Intelligence & Style Extraction",
            "Raw Footage Automated Scene Detection & Best Shot Selection",
            "AI Creative Director 3-Way Concept Synthesis (Epic, Social 9:16, Story)",
            "Epic Orchestral Music Scoring & Beat Drop Synchronization",
            "Cinematic Sound Design Layering & Voice Ducking (-14dB)",
            "Interactive Multi-Track Visual Timeline Schema",
            "Quality Control Black-Frame & Audio-Clipping Validator",
        ],
    }


# ==========================================
# 1. Reference Intelligence Endpoints
# ==========================================

@router.post("/references/analyze")
def analyze_reference_video(
    payload: ReferenceAnalyzeRequest,
    membership=Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    """Module 1: Extract cinematic profile and style parameters from reference video."""
    analysis = CreativeStudioService.analyze_reference(
        title=payload.title,
        file_url=payload.file_url,
        duration_seconds=payload.duration_seconds,
        user_notes=payload.user_notes,
    )

    ref = ReferenceVideo(
        organization_id=_get_org_id(membership),
        title=payload.title,
        file_url=payload.file_url,
        duration_seconds=payload.duration_seconds,
        shot_count=analysis["shot_count"],
        pacing_cuts_per_minute=analysis["pacing_cuts_per_minute"],
        style_tags=json.dumps(analysis["style_tags"]),
        camera_movement_analysis=json.dumps(analysis["camera_movement"]),
        color_palette=json.dumps(analysis["color_palette"]),
        music_rhythm_analysis=json.dumps(analysis["music_rhythm"]),
        storytelling_structure=json.dumps(analysis["storytelling_structure"]),
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)

    return {
        "id": ref.id,
        "title": ref.title,
        "analysis": analysis,
        "created_at": ref.created_at.isoformat(),
    }


@router.get("/references")
def list_reference_videos(
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    """List all registered reference videos with their extracted style profiles."""
    query = db.query(ReferenceVideo)
    org_id = _get_org_id(membership)
    if org_id:
        query = query.filter(ReferenceVideo.organization_id == org_id)
    refs = query.order_by(ReferenceVideo.created_at.desc()).all()
    results = []
    for r in refs:
        results.append({
            "id": r.id,
            "title": r.title,
            "file_url": r.file_url,
            "duration_seconds": r.duration_seconds,
            "shot_count": r.shot_count,
            "pacing_cuts_per_minute": r.pacing_cuts_per_minute,
            "style_tags": json.loads(r.style_tags) if r.style_tags else [],
            "color_palette": json.loads(r.color_palette) if r.color_palette else {},
            "created_at": r.created_at.isoformat(),
        })
    return results


# ==========================================
# 2. Raw Footage Intelligence Endpoints
# ==========================================

@router.post("/footages/scan")
def scan_raw_footage(
    payload: FootageScanRequest,
    membership=Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    """Module 2: Process raw video clip, detect scenes, stability, and highlights."""
    scanned = CreativeStudioService.scan_footage(
        filename=payload.filename,
        file_url=payload.file_url,
        duration_seconds=payload.duration_seconds,
        resolution=payload.resolution,
    )

    footage = RawFootage(
        organization_id=_get_org_id(membership),
        filename=payload.filename,
        file_url=payload.file_url,
        duration_seconds=payload.duration_seconds,
        resolution=payload.resolution,
        quality_score=scanned["quality_score"],
        stability_score=scanned["stability_score"],
        blur_detected=scanned["blur_detected"],
        camera_movement=scanned["camera_movement"],
        tags=json.dumps(scanned["tags"]),
        is_b_roll=scanned["is_b_roll"],
        selected_highlight=scanned["selected_highlight"],
        scenes_json=json.dumps(scanned["scenes"]),
    )
    db.add(footage)
    db.commit()
    db.refresh(footage)

    return {
        "id": footage.id,
        "filename": footage.filename,
        "scanned_data": scanned,
        "created_at": footage.created_at.isoformat(),
    }


@router.get("/footages")
def list_raw_footages(
    highlights_only: bool = Query(default=False),
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    """List raw footages with optional filter for AI-selected highlights."""
    query = db.query(RawFootage)
    org_id = _get_org_id(membership)
    if org_id:
        query = query.filter(RawFootage.organization_id == org_id)
    if highlights_only:
        query = query.filter(RawFootage.selected_highlight == True)  # noqa: E712
    footages = query.order_by(RawFootage.created_at.desc()).all()

    results = []
    for f in footages:
        results.append({
            "id": f.id,
            "filename": f.filename,
            "file_url": f.file_url,
            "duration_seconds": f.duration_seconds,
            "resolution": f.resolution,
            "quality_score": f.quality_score,
            "stability_score": f.stability_score,
            "camera_movement": f.camera_movement,
            "selected_highlight": f.selected_highlight,
            "tags": json.loads(f.tags) if f.tags else [],
            "scenes": json.loads(f.scenes_json) if f.scenes_json else [],
            "created_at": f.created_at.isoformat(),
        })
    return results


# ==========================================
# 3. AI Creative Director Endpoints
# ==========================================

@router.post("/director/generate-concepts")
def generate_concepts(
    payload: GenerateConceptsRequest,
    membership=Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    """Module 3: Synthesize 3 creative direction concepts with shot decisions."""
    concepts_data = CreativeStudioService.generate_creative_concepts(
        episode_title=payload.episode_title,
        logline=payload.logline,
        target_duration_seconds=payload.target_duration_seconds,
    )

    created = []
    for c in concepts_data:
        concept = CreativeDirectorConcept(
            organization_id=_get_org_id(membership),
            concept_type=c["concept_type"],
            title=c["title"],
            logline=c["logline"],
            target_duration_seconds=c["target_duration_seconds"],
            pacing_profile=c["pacing_profile"],
            recommended_bgm_genre=c["recommended_bgm_genre"],
            emotional_arc=json.dumps(c["emotional_arc"]),
            shot_decisions=json.dumps(c["shot_decisions"]),
            status="draft",
        )
        db.add(concept)
        db.commit()
        db.refresh(concept)
        created.append({
            "id": concept.id,
            **c,
            "status": concept.status,
            "created_at": concept.created_at.isoformat(),
        })

    return created


@router.get("/director/concepts")
def list_concepts(
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    """List all AI Creative Director concepts."""
    query = db.query(CreativeDirectorConcept)
    org_id = _get_org_id(membership)
    if org_id:
        query = query.filter(CreativeDirectorConcept.organization_id == org_id)
    concepts = query.order_by(CreativeDirectorConcept.created_at.desc()).all()
    results = []
    for c in concepts:
        results.append({
            "id": c.id,
            "concept_type": c.concept_type,
            "title": c.title,
            "logline": c.logline,
            "target_duration_seconds": c.target_duration_seconds,
            "pacing_profile": c.pacing_profile,
            "recommended_bgm_genre": c.recommended_bgm_genre,
            "emotional_arc": json.loads(c.emotional_arc) if c.emotional_arc else [],
            "shot_decisions": json.loads(c.shot_decisions) if c.shot_decisions else [],
            "status": c.status,
            "created_at": c.created_at.isoformat(),
        })
    return results


# ==========================================
# 4. Music & Sound Design Endpoints
# ==========================================

@router.get("/audio/music-catalog")
def get_music_catalog():
    """Module 5: Return curated cinematic orchestral music with beat grids."""
    return CreativeStudioService.get_curated_music_catalog()


@router.get("/audio/sfx-catalog")
def get_sfx_catalog():
    """Module 6: Return cinematic sound design elements (impacts, whooshes, risers)."""
    return CreativeStudioService.get_curated_sfx_catalog()


# ==========================================
# 5. Timeline Studio Endpoints
# ==========================================

@router.post("/timeline/save")
def save_timeline_project(
    payload: TimelineSaveRequest,
    membership=Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    """Module 7: Persist or update multi-track visual timeline representation."""
    timeline = TimelineProject(
        organization_id=_get_org_id(membership),
        title=payload.title,
        target_aspect_ratio=payload.target_aspect_ratio,
        tracks_json=json.dumps(payload.tracks),
        duration_seconds=payload.duration_seconds,
        render_status="draft",
    )
    db.add(timeline)
    db.commit()
    db.refresh(timeline)

    return {
        "id": timeline.id,
        "title": timeline.title,
        "aspect_ratio": timeline.target_aspect_ratio,
        "duration_seconds": timeline.duration_seconds,
        "render_status": timeline.render_status,
        "created_at": timeline.created_at.isoformat(),
    }


@router.get("/timeline/{timeline_id}")
def get_timeline_project(
    timeline_id: str,
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    """Fetch multi-track timeline by ID."""
    query = db.query(TimelineProject).filter(TimelineProject.id == timeline_id)
    org_id = _get_org_id(membership)
    if org_id:
        query = query.filter(TimelineProject.organization_id == org_id)
    timeline = query.first()
    if not timeline:
        raise HTTPException(status_code=404, detail="Timeline project not found")

    return {
        "id": timeline.id,
        "title": timeline.title,
        "target_aspect_ratio": timeline.target_aspect_ratio,
        "duration_seconds": timeline.duration_seconds,
        "tracks": json.loads(timeline.tracks_json) if timeline.tracks_json else {},
        "render_status": timeline.render_status,
        "created_at": timeline.created_at.isoformat(),
    }


# ==========================================
# 6. Quality Control Endpoints
# ==========================================

@router.post("/qc/evaluate")
def evaluate_timeline_quality(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Module 8: Validate A/V sync, clipping, black frames, subtitle readability."""
    tracks = payload.get("tracks", {})
    qc_result = CreativeStudioService.evaluate_quality_control(tracks)

    timeline_id = payload.get("timeline_id")
    if timeline_id:
        report = QualityControlReport(
            timeline_id=timeline_id,
            overall_score=qc_result["overall_score"],
            black_frames_detected=qc_result["black_frames_detected"],
            frozen_frames_detected=qc_result["frozen_frames_detected"],
            audio_clipping_events=qc_result["audio_clipping_events"],
            av_sync_offset_ms=qc_result["av_sync_offset_ms"],
            subtitle_sync_status=qc_result["subtitle_sync_status"],
            passed=qc_result["passed"],
            issues_json=json.dumps(qc_result["issues"]),
        )
        db.add(report)
        db.commit()
        db.refresh(report)

    return qc_result
