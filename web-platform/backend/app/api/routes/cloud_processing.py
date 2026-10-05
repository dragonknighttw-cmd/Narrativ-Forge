import base64
import hashlib
import hmac
import json
import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import get_db
from ...models import Episode
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


class WhisperTokenRequest(BaseModel):
    episode_id: str


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

    now = int(time.time())
    claims = {
        "sub": str(user["id"]),
        "episode_id": episode.id,
        "exp": now + settings.cloudflare_whisper_token_ttl_seconds,
    }
    return {
        "worker_url": settings.cloudflare_whisper_worker_url.rstrip("/"),
        "token": _sign(claims),
        "expires_at": claims["exp"],
    }
