import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import get_db
from ...models import GoogleDriveConnection
from ..dependencies import get_current_user, require_roles

GOOGLE_SCOPE = "https://www.googleapis.com/auth/drive.file"
router = APIRouter(prefix="/drive/google", tags=["google-drive"])

def _fernet():
    if not settings.oauth_encryption_key:
        raise HTTPException(status_code=503, detail="Drive disconnected: OAuth encryption key is not configured")
    try:
        return Fernet(settings.oauth_encryption_key.encode())
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Drive disconnected: invalid OAuth encryption key") from exc

def _state(email: str):
    payload = f"{email}|{int(time.time())}"
    key = settings.oauth_encryption_key.encode()
    sig = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{sig}".encode()).decode()

def _verify_state(value: str):
    try:
        raw = base64.urlsafe_b64decode(value.encode()).decode()
        email, timestamp, signature = raw.rsplit("|", 2)
        payload = f"{email}|{timestamp}"
        if time.time() - int(timestamp) > 600:
            raise ValueError("expired")
        expected = hmac.new(settings.oauth_encryption_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid")
        return email
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state") from exc

@router.get("/status")
def google_status(user=Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.query(GoogleDriveConnection).filter(GoogleDriveConnection.user_email == user["email"]).first()
    return {"connected": bool(item), "provider": "google_drive", "scope": item.scope if item else None}

@router.get("/start")
def google_start(user=Depends(get_current_user)):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=503, detail="Drive disconnected: Google OAuth credentials are not configured")
    if not settings.oauth_encryption_key:
        raise HTTPException(status_code=503, detail="Drive disconnected: OAuth encryption key is not configured")
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": GOOGLE_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": _state(user["email"]),
    }
    return {"authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)}

@router.get("/callback")
async def google_callback(code: str, state: str, db: Session = Depends(get_db)):
    email = _verify_state(state)
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=503, detail="Google OAuth credentials are not configured")
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code, "client_id": settings.google_client_id, "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri, "grant_type": "authorization_code",
        })
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Google OAuth token exchange failed")
    token = response.json()
    refresh_token = token.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=502, detail="Google did not return a refresh token")
    f = _fernet()
    item = db.query(GoogleDriveConnection).filter(GoogleDriveConnection.user_email == email).first()
    if not item:
        item = GoogleDriveConnection(user_email=email, refresh_token_encrypted=f.encrypt(refresh_token.encode()).decode())
        db.add(item)
    else:
        item.refresh_token_encrypted = f.encrypt(refresh_token.encode()).decode()
    access_token = token.get("access_token")
    item.access_token_encrypted = f.encrypt(access_token.encode()).decode() if access_token else None
    item.expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(token.get("expires_in", 3600))) if access_token else None
    item.scope = token.get("scope", GOOGLE_SCOPE)
    db.commit()
    return {"connected": True, "provider": "google_drive", "message": "Google Drive connected. Return to Narrativ Forge."}

async def access_token_for(user_email: str, db: Session):
    item = db.query(GoogleDriveConnection).filter(GoogleDriveConnection.user_email == user_email).first()
    if not item:
        raise HTTPException(status_code=409, detail="Drive disconnected")
    f = _fernet()
    if item.access_token_encrypted and item.expires_at and item.expires_at > datetime.now(timezone.utc) + timedelta(seconds=60):
        return f.decrypt(item.access_token_encrypted.encode()).decode()
    refresh = f.decrypt(item.refresh_token_encrypted.encode()).decode()
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post("https://oauth2.googleapis.com/token", data={
            "client_id": settings.google_client_id, "client_secret": settings.google_client_secret,
            "refresh_token": refresh, "grant_type": "refresh_token",
        })
    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail="Google access token refresh failed")
    token = response.json()
    access = token["access_token"]
    item.access_token_encrypted = f.encrypt(access.encode()).decode()
    item.expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(token.get("expires_in", 3600)))
    db.commit()
    return access
