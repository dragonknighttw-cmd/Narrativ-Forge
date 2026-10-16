from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import update
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Episode, Season, Series
from ..dependencies import get_current_membership, get_current_user, require_roles

router = APIRouter(prefix="/episodes", tags=["episodes"])

VALID_STATUSES = {
    "idea","planned","script_draft","script_review","assets_needed","in_production",
    "processing","subtitle_review","needs_approval","approved","exporting","exported",
    "archived","rejected","failed"
}
STEP_BY_STATUS = {
    "idea": "idea", "planned": "structure", "script_draft": "script", "script_review": "script",
    "assets_needed": "assets", "in_production": "production", "processing": "processing",
    "subtitle_review": "subtitle", "needs_approval": "review", "approved": "review",
    "exporting": "output", "exported": "output", "archived": "output", "rejected": "review", "failed": "processing",
}

STATUS_TRANSITIONS = {
    "idea": {"planned"},
    "planned": {"script_draft"},
    "script_draft": {"script_review"},
    "script_review": {"assets_needed", "script_draft"},
    "assets_needed": {"in_production"},
    "in_production": {"processing"},
    "processing": {"subtitle_review"},
    "subtitle_review": {"needs_approval", "in_production"},
    "needs_approval": {"approved", "in_production"},
    "approved": {"exporting"},
    "exporting": {"exported", "failed"},
    "exported": {"archived"},
    "archived": set(),
    "rejected": set(),
    "failed": {"processing"},
}

class EpisodeCreate(BaseModel):
    public_id: str | None = Field(default=None, max_length=40)
    series_id: str
    season_id: str | None = None
    episode_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    synopsis: str | None = None
    target_duration_seconds: int = Field(default=180, ge=1)

class EpisodeUpdate(BaseModel):
    season_id: str | None = None
    episode_number: int | None = Field(default=None, ge=1)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    category: str | None = Field(default=None, max_length=100)
    synopsis: str | None = None
    target_duration_seconds: int | None = Field(default=None, ge=1)
    actual_duration_seconds: int | None = Field(default=None, ge=0)
    status: str | None = None
    current_step: str | None = Field(default=None, max_length=40)
    expected_row_version: int = Field(ge=1)

def generated_public_id(db: Session) -> str:
    prefix = date.today().strftime("nar_%Y%m%d_")
    count = db.query(Episode).filter(Episode.public_id.like(prefix + "%")).count()
    return f"{prefix}{count + 1:04d}"

def validate_structure(db: Session, series_id: str, season_id: str | None, organization_id: str | None = None):
    series = db.query(Series).filter(Series.id == series_id, *( [Series.organization_id == organization_id] if organization_id else [] )).first()
    if not series:
        raise HTTPException(status_code=404, detail="Series not found")
    if season_id:
        season = db.get(Season, season_id)
        if not season or season.series_id != series_id:
            raise HTTPException(status_code=400, detail="Season does not belong to this series")

@router.get("")
def list_episodes(membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    return db.query(Episode).filter(Episode.organization_id == membership.organization_id).order_by(Episode.created_at.desc()).all()

@router.post("", status_code=201)
def create_episode(payload: EpisodeCreate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    validate_structure(db, payload.series_id, payload.season_id, membership.organization_id)
    if payload.season_id and db.query(Episode).filter(Episode.season_id == payload.season_id, Episode.episode_number == payload.episode_number).first():
        raise HTTPException(status_code=409, detail="Episode number already exists in this season")
    public_id = payload.public_id or generated_public_id(db)
    if db.query(Episode).filter(Episode.public_id == public_id).first():
        raise HTTPException(status_code=409, detail="Public ID already exists")
    item = Episode(organization_id=membership.organization_id, public_id=public_id, **payload.model_dump(exclude={"public_id"}))
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/{episode_id}")
def get_episode(episode_id: str, membership=Depends(get_current_membership), db: Session = Depends(get_db)):
    item = db.query(Episode).filter(Episode.id == episode_id, Episode.organization_id == membership.organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Episode not found")
    return item

@router.patch("/{episode_id}")
def update_episode(episode_id: str, payload: EpisodeUpdate, membership=Depends(get_current_membership), _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.query(Episode).filter(Episode.id == episode_id, Episode.organization_id == membership.organization_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Episode not found")

    expected_row_version = payload.expected_row_version
    data = payload.model_dump(exclude={"expected_row_version"}, exclude_unset=True)
    if "status" in data:
        status = data["status"]
        if status not in VALID_STATUSES:
            raise HTTPException(status_code=400, detail="Invalid episode status")
        if status != item.status and status not in STATUS_TRANSITIONS.get(item.status, set()):
            raise HTTPException(status_code=409, detail=f"Invalid status transition: {item.status} -> {status}")
    season_id = data.get("season_id", item.season_id)
    validate_structure(db, item.series_id, season_id, membership.organization_id)
    number = data.get("episode_number", item.episode_number)
    if season_id and db.query(Episode).filter(
        Episode.id != item.id,
        Episode.season_id == season_id,
        Episode.episode_number == number,
    ).first():
        raise HTTPException(status_code=409, detail="Episode number already exists in this season")

    if "status" in data:
        data["current_step"] = STEP_BY_STATUS[data["status"]]

    data["row_version"] = Episode.row_version + 1
    data["updated_at"] = datetime.now(timezone.utc)
    result = db.execute(
        update(Episode)
        .where(Episode.id == episode_id, Episode.row_version == expected_row_version)
        .values(**data)
    )
    if result.rowcount != 1:
        db.rollback()
        current = db.get(Episode, episode_id)
        if not current:
            raise HTTPException(status_code=404, detail="Episode not found")
        raise HTTPException(
            status_code=409,
            detail={
                "code": "STALE_ROW_VERSION",
                "message": "Episode was modified by another request",
                "current": jsonable_encoder(current),
            },
        )

    db.commit()
    db.refresh(item)
    return item


class VoiceoverGenerateRequest(BaseModel):
    voice: str = "burmese_female"
    text: str | None = None
    rate: str = "+0%"
    pitch: str = "+0Hz"


class StoryboardGenerateRequest(BaseModel):
    aspect_ratio: str = "9:16"
    model: str = "flux"
    enhance: bool = True


@router.post("/{episode_id}/generate-voiceover")
async def generate_episode_voiceover(
    episode_id: str,
    payload: VoiceoverGenerateRequest,
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    """Synthesize voiceover using zero-cost Microsoft Edge Neural TTS."""
    from ...services.edge_tts_service import EdgeTTSService
    from ...services.telegram import send_notification
    from ...models import Asset, Scene

    episode = db.query(Episode).filter(Episode.id == episode_id, Episode.organization_id == membership.organization_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    # Determine narration script text
    narration_text = payload.text
    if not narration_text:
        # Build narration from scenes dialogue/description or synopsis
        scenes = db.query(Scene).filter(Scene.episode_id == episode_id).order_by(Scene.scene_number).all()
        scene_dialogues = [s.dialogue or s.description for s in scenes if s.dialogue or s.description]
        if scene_dialogues:
            narration_text = " ".join(scene_dialogues)
        elif episode.synopsis:
            narration_text = episode.synopsis
        else:
            narration_text = f"Welcome to episode {episode.episode_number}: {episode.title}."

    output_dir = Path("storage/uploads/voiceovers")
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"voiceover_{episode_id}_{payload.voice}.mp3"
    filepath = output_dir / filename

    result = await EdgeTTSService.synthesize_to_file(
        text=narration_text,
        output_file_path=filepath,
        voice=payload.voice,
        rate=payload.rate,
        pitch=payload.pitch,
    )

    # Register as asset
    existing_asset_count = db.query(Asset).filter(Asset.episode_id == episode_id).count()
    asset = Asset(
        episode_id=episode_id,
        asset_type="audio",
        original_filename=filename,
        storage_provider="local",
        local_path=str(filepath),
        mime_type="audio/mpeg",
        file_size_bytes=result["file_size_bytes"],
        version=existing_asset_count + 1,
        status="ready",
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    # Trigger Telegram notification if configured
    await send_notification(
        title=f"Voiceover Generated: {episode.title}",
        details=f"🎙️ Voice: {result['voice']}\n📊 Size: {result['file_size_bytes']} bytes\n🆔 Asset: <code>{asset.id}</code>",
        status="SUCCESS",
    )

    return {
        "status": "success",
        "asset_id": asset.id,
        "voice": result["voice"],
        "file_path": str(filepath),
        "vtt_subtitles": result.get("vtt_subtitles", ""),
    }


@router.post("/{episode_id}/generate-storyboards")
async def generate_episode_storyboards(
    episode_id: str,
    payload: StoryboardGenerateRequest,
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    """Generate 9:16 vertical or 16:9 cinematic storyboard visuals via Pollinations FLUX."""
    from ...services.storyboard_generator import StoryboardGeneratorService
    from ...services.telegram import send_notification
    from ...models import Asset, Scene

    episode = db.query(Episode).filter(Episode.id == episode_id, Episode.organization_id == membership.organization_id).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    scenes = db.query(Scene).filter(Scene.episode_id == episode_id).order_by(Scene.scene_number).all()
    if not scenes:
        # Generate at least one storyboard for the episode overall
        fallback_prompt = f"Episode {episode.episode_number} of {episode.title}. {episode.synopsis or 'Cinematic narrative scene.'}"
        scenes = [Scene(id=None, scene_number=1, purpose=episode.title, description=fallback_prompt)]

    output_dir = Path("storage/uploads/storyboards")
    output_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    w, h = (720, 1280) if payload.aspect_ratio == "9:16" else (1280, 720)

    for sc in scenes:
        prompt_text = sc.description or sc.purpose or f"Scene {sc.scene_number} for {episode.title}"
        filename = f"storyboard_{episode_id}_s{sc.scene_number}_{payload.aspect_ratio.replace(':', 'x')}.jpg"
        filepath = output_dir / filename

        gen_result = await StoryboardGeneratorService.generate_and_save_scene(
            prompt=prompt_text,
            output_file_path=filepath,
            aspect_ratio=payload.aspect_ratio,
            model=payload.model,
        )

        existing_asset_count = db.query(Asset).filter(Asset.episode_id == episode_id).count()
        asset = Asset(
            episode_id=episode_id,
            scene_id=sc.id if sc.id else None,
            asset_type="storyboard",
            original_filename=filename,
            storage_provider="local",
            local_path=str(filepath),
            mime_type="image/jpeg",
            file_size_bytes=gen_result["file_size_bytes"],
            width=w,
            height=h,
            version=existing_asset_count + 1,
            status="ready",
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)

        generated.append({
            "scene_number": sc.scene_number,
            "asset_id": asset.id,
            "image_url": gen_result["image_url"],
            "file_path": str(filepath),
        })

    # Trigger Telegram notification
    await send_notification(
        title=f"Storyboards Generated: {episode.title}",
        details=f"🎨 Generated {len(generated)} {payload.aspect_ratio} storyboard visuals via FLUX.",
        status="SUCCESS",
    )

    return {
        "status": "success",
        "episode_id": episode_id,
        "aspect_ratio": payload.aspect_ratio,
        "count": len(generated),
        "storyboards": generated,
    }

