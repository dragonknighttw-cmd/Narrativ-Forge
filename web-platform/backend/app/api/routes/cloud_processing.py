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


def _verify_signed_payload(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid Whisper usage key")
    try:
        encoded, supplied = parts
        expected = hmac.new(
            settings.cloudflare_whisper_shared_secret.encode(),
            encoded.encode(),
            hashlib.sha256,
        ).digest()
        supplied_bytes = base64.urlsafe_b64decode(supplied + "=" * (-len(supplied) % 4))
        if not hmac.compare_digest(expected, supplied_bytes):
            raise ValueError("signature mismatch")
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode())
    except (ValueError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail="Invalid Whisper usage key") from exc
    if not isinstance(payload, dict) or payload.get("purpose") != "usage":
        raise HTTPException(status_code=400, detail="Invalid Whisper usage key")
    if int(payload.get("exp", 0)) <= int(time.time()):
        raise HTTPException(status_code=400, detail="Whisper usage key expired")
    return payload


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
    estimated_audio_seconds: int = Field(default=1, ge=1, le=86400)


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
        return {
            "worker_url": "",
            "token": "",
            "expires_at": 0,
            "usage_key": "",
            "warning": True,
            "fallback_required": True,
            "usage": usage,
        }

    now = int(time.time())
    claims = {
        "sub": str(user["id"]),
        "episode_id": episode.id,
        "exp": now + settings.cloudflare_whisper_token_ttl_seconds,
        "jti": str(uuid4()),
        "max_audio_seconds": payload.estimated_audio_seconds,
    }
    usage_key = _sign({
        "purpose": "usage",
        "sub": str(user["id"]),
        "episode_id": episode.id,
        "exp": claims["exp"],
        "jti": claims["jti"],
        "max_audio_seconds": payload.estimated_audio_seconds,
    })
    return {
        "worker_url": settings.cloudflare_whisper_worker_url.rstrip("/"),
        "token": _sign(claims),
        "expires_at": claims["exp"],
        "usage_key": usage_key,
        "usage": usage,
        "warning": ratio >= settings.cloudflare_whisper_warning_threshold,
        "fallback_required": False,
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
    user: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    usage_claims = _verify_signed_payload(payload.usage_key)
    if usage_claims.get("sub") != str(user["id"]):
        raise HTTPException(status_code=403, detail="Whisper usage key does not belong to the current user")
    if payload.audio_seconds > int(usage_claims.get("max_audio_seconds", 0)):
        raise HTTPException(status_code=400, detail="Recorded audio exceeds the signed Whisper estimate")
    key = f"cloud-whisper:{usage_claims['jti']}"
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


@router.post("/groq-transcribe")
async def transcribe_with_groq(
    episode_id: str,
    membership=Depends(get_current_membership),
    _: dict = Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    """Fallback STT: Call Groq whisper-large-v3 for ultra-fast, zero-quota-drain transcription."""
    import os
    import httpx
    from ...models import Asset

    _episode_or_404 = None
    episode = db.query(Episode).filter(
        Episode.id == episode_id,
        Episode.organization_id == membership.organization_id,
    ).first()
    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found")

    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_key or groq_key.startswith("your_"):
        raise HTTPException(status_code=503, detail="Groq API key is not configured for Whisper fallback")

    # Find audio asset for episode
    audio_asset = db.query(Asset).filter(
        Asset.episode_id == episode.id,
        Asset.asset_type.in_(["audio", "audio_wav", "voiceover", "draft_video"]),
    ).first()
    if not audio_asset or not audio_asset.storage_path:
        raise HTTPException(status_code=422, detail="No audio asset available for Groq Whisper transcription")

    audio_path = audio_asset.storage_path
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found in storage")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            with open(audio_path, "rb") as f:
                files = {"file": (os.path.basename(audio_path), f, "audio/wav")}
                data = {
                    "model": "whisper-large-v3",
                    "response_format": "vtt",
                    "temperature": "0.0",
                }
                res = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {groq_key}"},
                    files=files,
                    data=data,
                )
                if res.status_code != 200:
                    raise HTTPException(status_code=res.status_code, detail=f"Groq Whisper transcription failed: {res.text[:200]}")
                vtt_text = res.text
                return {"provider": "groq_whisper", "model": "whisper-large-v3", "vtt": vtt_text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Groq Whisper request error: {str(exc)}")

