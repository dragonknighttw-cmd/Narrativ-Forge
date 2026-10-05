import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import get_db
from ...models import Episode, UsageEvent
from ..dependencies import get_current_membership, require_roles

router = APIRouter(prefix="/cloud-processing", tags=["cloud-processing"])


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _sign(payload: dict) -> str:
    encoded = _b64(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode())
    signature = hmac.new(
        settings.cloudflare_whisper_shared_secret.encode(),
        encoded.encode(),
        hashlib.sha256,
    ).digest()
    return encoded + "." + _b64(signature)


def _daily_usage(db: Session, organization_id: str) -> dict:
    today = datetime.now(timezone.utc).date()
    rows = db.query(UsageEvent).filter(
        UsageEvent.organization_id == organization_id,
        UsageEvent.metric == "cloudflare_whisper_audio_seconds",
    ).all()
    seconds = sum(
        row.quantity
        for row in rows
        if row.created_at and row.created_at.astimezone(timezone.utc).date() == today
    )
    neurons = (seconds / 60.0) * settings.cloudflare_whisper_neurons_per_audio_minute
    budget = float(settings.cloudflare_whisper_daily_neuron_budget or 1)
    ratio = neurons / budget
    return {
        "audio_seconds": seconds,
        "audio_minutes": round(seconds / 60.0, 2),
        "estimated_neurons": round(neurons, 2),
        "daily_neuron_budget": settings.cloudflare_whisper_daily_neuron_budget,
        "usage_ratio": round(ratio, 4),
        "warning": ratio >= settings.cloudflare_whisper_warning_threshold,
        "fallback_required": ratio >= settings.cloudflare_whisper_fallback_threshold,
        "date_utc": today.isoformat(),
    }


class WhisperTokenRequest(BaseModel):
    episode_id: str
    estimated_audio_seconds: int = Field(default=0, ge=0, le=86400)


class WhisperUsageRequest(BaseModel):
    usage_key: str
    audio_seconds: int = Field(gt=0, le=86400)


@router.post("/whisper-token")
def create_whisper_token(
    payload: WhisperTokenRequest,
    membership=Depends(get_current_membership),
    user: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    episode = db.query(Episode).filter(
        Episode.id == payload.episode_id,
        Episode.organization_id == membership.organization_id,
    ).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")
    if not settings.cloudflare_whisper_worker_url or not settings.cloudflare_whisper_shared_secret:
        raise HTTPException(status_code=503, detail="Cloudflare Whisper offload is not configured")

    usage = _daily_usage(db, membership.organization_id)
    projected_neurons = usage["estimated_neurons"] + (
        payload.estimated_audio_seconds / 60.0
    ) * settings.cloudflare_whisper_neurons_per_audio_minute
    ratio = projected_neurons / float(settings.cloudflare_whisper_daily_neuron_budget or 1)
    if ratio >= settings.cloudflare_whisper_fallback_threshold:
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Cloudflare Whisper daily safety budget is near exhaustion; use Celery fallback.",
                "fallback_required": True,
                "usage": usage,
            },
        )

    now = int(time.time())
    claims = {
        "sub": str(user["id"]),
        "episode_id": episode.id,
        "exp": now + settings.cloudflare_whisper_token_ttl_seconds,
        "jti": str(uuid4()),
    }
    return {
        "worker_url": settings.cloudflare_whisper_worker_url.rstrip("/"),
        "token": _sign(claims),
        "expires_at": claims["exp"],
        "usage_key": claims["jti"],
        "usage": usage,
        "warning": ratio >= settings.cloudflare_whisper_warning_threshold,
    }


@router.get("/whisper-usage")
def whisper_usage(
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    return _daily_usage(db, membership.organization_id)


@router.post("/whisper-usage")
def record_whisper_usage(
    payload: WhisperUsageRequest,
    membership=Depends(get_current_membership),
    _: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    key = f"cloud-whisper:{payload.usage_key}"
    existing = db.query(UsageEvent).filter(UsageEvent.idempotency_key == key).first()
    if existing:
        return {"recorded": False, "usage": _daily_usage(db, membership.organization_id)}

    period = datetime.now(timezone.utc).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    db.add(UsageEvent(
        organization_id=membership.organization_id,
        metric="cloudflare_whisper_audio_seconds",
        quantity=payload.audio_seconds,
        unit="second",
        idempotency_key=key,
        period_start=period,
        metadata_json=json.dumps(
            {"usage_key": payload.usage_key},
            separators=(",", ":"),
        ),
    ))
    db.commit()
    return {"recorded": True, "usage": _daily_usage(db, membership.organization_id)}
