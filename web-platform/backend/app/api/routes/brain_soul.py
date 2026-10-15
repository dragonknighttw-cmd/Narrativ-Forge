"""Brain Soul Layer — REST endpoints for Narrativ Forge.

Soul File: personal context store that makes every AI interaction in
Narrativ aware of your storytelling style, current projects, genre
preferences, and narrative voice — without re-explaining every session.

Endpoints:
  GET    /api/v1/brain/soul/context           — list Soul File entries
  POST   /api/v1/brain/soul/context           — upsert entry
  DELETE /api/v1/brain/soul/context/{key}     — remove entry
  GET    /api/v1/brain/soul/context/prefix    — preview LLM system-prompt prefix
  GET    /api/v1/brain/soul/syntheses         — list weekly story synthesis snapshots
  POST   /api/v1/brain/soul/synthesize        — manually trigger synthesis
  GET    /api/v1/brain/soul/status            — health overview
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models.brain_soul import BrainSoulContext, BrainSoulSynthesis
from ..dependencies import get_current_user

logger = logging.getLogger("narrativ.brain_soul")

router = APIRouter(prefix="/brain/soul", tags=["brain-soul"])

# ── default Soul File entries ─────────────────────────────────────────────────
_SOUL_DEFAULTS = [
    ("creator_name",      "Narrativ Creator",        "Who is using this Narrativ Forge instance"),
    ("primary_genre",     "drama / thriller",         "Main storytelling genre"),
    ("narrative_voice",   "third person limited",     "Preferred narrative perspective"),
    ("writing_style",     "cinematic and concise",    "Tone and style for AI-generated content"),
    ("active_projects",   "current series in production", "High-level description of active work"),
    ("brain_purpose",     "Personal story brain — ideas, hooks, SEO, narrative synthesis", "What this brain layer is for"),
]


def _seed_defaults(db: Session) -> None:
    """Seed default Soul File entries once — never overwrites existing values."""
    for key, value, description in _SOUL_DEFAULTS:
        if db.query(BrainSoulContext).filter_by(context_key=key).first() is None:
            db.add(BrainSoulContext(
                context_key=key,
                context_value=value,
                description=description,
                updated_by="system",
            ))
    db.commit()


def _build_system_prefix(db: Session) -> str:
    """Build LLM system-prompt prefix from active Soul File entries."""
    try:
        rows = (
            db.query(BrainSoulContext)
            .filter_by(is_active=True)
            .order_by(BrainSoulContext.context_key)
            .all()
        )
        if not rows:
            return ""
        lines = ["[Personal Brain Context — Narrativ Forge]"]
        for r in rows:
            desc = f" ({r.description})" if r.description else ""
            lines.append(f"• {r.context_key}{desc}: {r.context_value}")
        lines.append("")
        return "\n".join(lines)
    except Exception:
        return ""


# ── request models ────────────────────────────────────────────────────────────

class ContextUpsert(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    value: str = Field(min_length=1, max_length=4000)
    description: str = Field(default="", max_length=500)


class SynthesizeRequest(BaseModel):
    topic: str = Field(default="story", min_length=1, max_length=80)
    force: bool = False


# ── context endpoints ─────────────────────────────────────────────────────────

@router.get("/context")
def list_context(
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return all Soul File entries."""
    _seed_defaults(db)
    rows = db.query(BrainSoulContext).order_by(BrainSoulContext.context_key).all()
    return {"entries": [r.to_dict() for r in rows], "total": len(rows)}


@router.post("/context", status_code=201)
def upsert_context(
    payload: ContextUpsert,
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Insert or update a Soul File entry."""
    existing = db.query(BrainSoulContext).filter_by(context_key=payload.key).first()
    if existing:
        existing.context_value = payload.value
        existing.description = payload.description
        existing.updated_by = "user"
        existing.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing)
        return {"entry": existing.to_dict()}
    entry = BrainSoulContext(
        context_key=payload.key,
        context_value=payload.value,
        description=payload.description,
        updated_by="user",
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"entry": entry.to_dict()}


@router.delete("/context/{key}")
def delete_context(
    key: str,
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Delete a Soul File entry by key."""
    entry = db.query(BrainSoulContext).filter_by(context_key=key).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"No soul context entry with key '{key}'")
    db.delete(entry)
    db.commit()
    return {"deleted": True, "key": key}


@router.get("/context/prefix")
def preview_prefix(
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Preview the LLM system-prompt prefix that Brain Soul injects."""
    prefix = _build_system_prefix(db)
    return {"prefix": prefix, "empty": not bool(prefix.strip())}


# ── synthesis endpoints ───────────────────────────────────────────────────────

@router.get("/syntheses")
def list_syntheses(
    limit: int = Query(default=20, ge=1, le=100),
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return recent weekly story synthesis snapshots, newest first."""
    rows = (
        db.query(BrainSoulSynthesis)
        .order_by(BrainSoulSynthesis.created_at.desc())
        .limit(limit)
        .all()
    )
    return {"syntheses": [r.to_dict() for r in rows], "total": len(rows)}


@router.post("/synthesize", status_code=202)
async def trigger_synthesis(
    payload: SynthesizeRequest,
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Manually trigger a weekly synthesis of recent story content.

    Reads ideas, series, episodes, and scenes created in the past 7 days,
    synthesises patterns and hooks with the LLM, then saves a snapshot.
    """
    now = datetime.now(timezone.utc)
    period_label = now.strftime("%Y-W%W")
    week_ago = now - timedelta(days=7)
    topic = payload.topic.strip() or "story"

    # Check for existing (skip unless force)
    if not payload.force:
        existing = (
            db.query(BrainSoulSynthesis)
            .filter_by(period_label=period_label, topic=topic)
            .first()
        )
        if existing:
            return {
                "status": "skipped",
                "reason": "Synthesis already exists for this period. Use force=true to regenerate.",
                "synthesis": existing.to_dict(),
            }

    # ── gather recent story content ───────────────────────────────────────────
    items: list[str] = []
    item_ids: list = []

    try:
        from ...models import Idea, Series, Episode, Scene
        for idea in (
            db.query(Idea)
            .filter(Idea.created_at >= week_ago)
            .order_by(Idea.created_at.desc())
            .limit(15)
            .all()
        ):
            snippet = (idea.concept or idea.hook or "")[:200].replace("\n", " ")
            items.append(f"[idea] {idea.title}: {snippet}")
            item_ids.append(f"idea:{idea.id}")

        for series in (
            db.query(Series)
            .filter(Series.created_at >= week_ago)
            .order_by(Series.created_at.desc())
            .limit(10)
            .all()
        ):
            items.append(f"[series] {series.title}: genre={getattr(series, 'genre', '')} status={getattr(series, 'status', '')}")
            item_ids.append(f"series:{series.id}")

        for ep in (
            db.query(Episode)
            .filter(Episode.created_at >= week_ago)
            .order_by(Episode.created_at.desc())
            .limit(15)
            .all()
        ):
            items.append(f"[episode] {getattr(ep, 'title', ep.id)}: ep#{getattr(ep, 'episode_number', '?')}")
            item_ids.append(f"episode:{ep.id}")

        for scene in (
            db.query(Scene)
            .filter(Scene.created_at >= week_ago)
            .order_by(Scene.created_at.desc())
            .limit(10)
            .all()
        ):
            snippet = (getattr(scene, 'description', '') or "")[:150].replace("\n", " ")
            items.append(f"[scene] {getattr(scene, 'title', scene.id)}: {snippet}")
            item_ids.append(f"scene:{scene.id}")
    except Exception as gather_exc:
        logger.warning("synthesize: gather failed — %s", gather_exc)

    if len(items) < 2:
        return {
            "status": "skipped",
            "reason": f"Only {len(items)} item(s) found in the past 7 days (need ≥ 2)",
            "period_label": period_label,
            "topic": topic,
        }

    # Build prompts with soul context injected
    soul_prefix = _build_system_prefix(db)
    combined = "\n".join(items)
    system_prompt = (
        f"{soul_prefix}"
        "You are a personal story intelligence assistant for a content creator. "
        "Based on the story content created this week, write a concise synthesis "
        "(250–400 words) covering:\n"
        "1. Key themes and narrative patterns that emerged\n"
        "2. Strongest hooks or ideas worth developing further\n"
        "3. SEO & audience angles to consider for upcoming content\n"
        "4. One or two concrete next actions\n\n"
        "Be specific and creative. Reference actual titles/ideas mentioned."
    )
    user_prompt = (
        f"Topic: {topic}\n"
        f"Period: {period_label} (past 7 days)\n"
        f"Items reviewed: {len(items)}\n\n"
        f"{combined}\n\nWrite the weekly story synthesis now."
    )

    # ── call LLM ──────────────────────────────────────────────────────────────
    synthesis_text: str
    provider: str | None = None
    try:
        from ...services.ai import ai_service  # Narrativ's AI service singleton
        synthesis_text = await ai_service.complete(
            system=system_prompt,
            user=user_prompt,
        )
        provider = getattr(ai_service, "last_provider", "narrativ_ai")
    except Exception:
        try:
            # Fallback: try production_intelligence service pattern
            from ...services.llm import call_llm
            synthesis_text = await call_llm(system_prompt, user_prompt)
            provider = "llm_service"
        except Exception as llm_exc:
            logger.warning("synthesize: all LLM paths failed — %s; extractive fallback", llm_exc)
            synthesis_text = "\n\n".join(f"• {item}" for item in items[:10])
            provider = "extractive_fallback"

    if not synthesis_text.strip():
        raise HTTPException(status_code=500, detail="AI returned empty synthesis text")

    # ── persist ───────────────────────────────────────────────────────────────
    if payload.force:
        db.query(BrainSoulSynthesis).filter_by(
            period_label=period_label, topic=topic
        ).delete()
        db.commit()

    snapshot = BrainSoulSynthesis(
        period_label=period_label,
        period_start=week_ago,
        period_end=now,
        topic=topic,
        synthesis_text=synthesis_text.strip(),
        source_item_ids=json.dumps(item_ids),
        item_count=len(item_ids),
        provider=provider,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "status": "created",
        "synthesis": snapshot.to_dict(),
        "item_count": len(items),
        "provider": provider,
    }


# ── status endpoint ───────────────────────────────────────────────────────────

@router.get("/status")
def soul_status(
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Health overview for the Brain Soul layer."""
    context_count = 0
    synthesis_count = 0
    latest_at: str | None = None
    tables_ready = False

    try:
        context_count = db.query(BrainSoulContext).filter_by(is_active=True).count()
        synthesis_count = db.query(BrainSoulSynthesis).count()
        latest = (
            db.query(BrainSoulSynthesis)
            .order_by(BrainSoulSynthesis.created_at.desc())
            .first()
        )
        if latest and latest.created_at:
            latest_at = latest.created_at.isoformat()
        tables_ready = True
    except Exception:
        pass

    return {
        "tables_ready": tables_ready,
        "active_context_entries": context_count,
        "total_syntheses": synthesis_count,
        "latest_synthesis_at": latest_at,
    }
