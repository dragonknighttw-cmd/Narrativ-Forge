import base64
import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from ...core.config import settings
from ...db import get_db
from ...models import GoogleDriveConnection, OrganizationMembership, User
from ..dependencies import get_current_user, require_roles
from ..routes.phase4 import current_membership

GOOGLE_SCOPE = "https://www.googleapis.com/auth/drive.file"
router = APIRouter(prefix="/drive/google", tags=["google-drive"])

def _fernet():
    if not settings.oauth_encryption_key:
        raise HTTPException(status_code=503, detail="Drive disconnected: OAuth encryption key is not configured")
    try:
        return Fernet(settings.oauth_encryption_key.encode())
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Drive disconnected: invalid OAuth encryption key") from exc

_OAUTH_STATE_COOKIE = "nf_google_oauth_state"
_OAUTH_STATE_COOKIE_PATH = "/api/v1/drive/google/callback"

def _state(email: str, organization_id: str, nonce: str):
    payload = f"{email}|{organization_id}|{int(time.time())}|{nonce}"
    key = settings.oauth_encryption_key.encode()
    sig = hmac.new(key, payload.encode(), hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(f"{payload}|{sig}".encode()).decode()

def _verify_state(value: str):
    try:
        padded = value + "=" * (-len(value) % 4)
        raw = base64.urlsafe_b64decode(padded.encode()).decode()
        email, organization_id, timestamp, nonce, signature = raw.rsplit("|", 4)
        payload = f"{email}|{organization_id}|{timestamp}|{nonce}"
        if time.time() - int(timestamp) > 600 or int(timestamp) > int(time.time()) + 60:
            raise ValueError("expired")
        if not nonce or len(nonce) < 32:
            raise ValueError("invalid nonce")
        expected = hmac.new(settings.oauth_encryption_key.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid")
        return email, organization_id, nonce
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state") from exc

@router.get("/status")
def google_status(user=Depends(require_roles("owner", "editor")), membership=Depends(current_membership), db: Session = Depends(get_db)):
    item = db.query(GoogleDriveConnection).filter(GoogleDriveConnection.user_email == user["email"], GoogleDriveConnection.organization_id == membership.organization_id).first()
    return {"connected": bool(item), "provider": "google_drive", "scope": item.scope if item else None}

@router.get("/start")
def google_start(
    response: Response,
    user=Depends(require_roles("owner", "editor")),
    membership=Depends(current_membership),
):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=503, detail="Drive disconnected: Google OAuth credentials are not configured")
    if not settings.oauth_encryption_key:
        raise HTTPException(status_code=503, detail="Drive disconnected: OAuth encryption key is not configured")
    nonce = secrets.token_urlsafe(32)
    response.set_cookie(
        key=_OAUTH_STATE_COOKIE,
        value=nonce,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        max_age=600,
        path=_OAUTH_STATE_COOKIE_PATH,
    )
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": GOOGLE_SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": _state(user["email"], membership.organization_id, nonce),
    }
    return {"authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)}

@router.get("/callback")
async def google_callback(
    code: str,
    state: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    email, organization_id, nonce = _verify_state(state)
    cookie_nonce = request.cookies.get(_OAUTH_STATE_COOKIE, "")
    if not cookie_nonce or not hmac.compare_digest(cookie_nonce, nonce):
        raise HTTPException(status_code=400, detail="OAuth state does not match this browser session")
    response.delete_cookie(
        key=_OAUTH_STATE_COOKIE,
        path=_OAUTH_STATE_COOKIE_PATH,
        secure=settings.session_cookie_secure,
        httponly=True,
        samesite="lax",
    )
    member = db.query(OrganizationMembership).join(User, User.id == OrganizationMembership.user_id).filter(
        User.email == email, OrganizationMembership.organization_id == organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="Google Drive OAuth workspace membership is no longer valid")
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
    item = db.query(GoogleDriveConnection).filter(GoogleDriveConnection.user_email == email, GoogleDriveConnection.organization_id == organization_id).first()
    if not item:
        item = GoogleDriveConnection(organization_id=organization_id, user_email=email, refresh_token_encrypted=f.encrypt(refresh_token.encode()).decode())
        db.add(item)
    else:
        item.refresh_token_encrypted = f.encrypt(refresh_token.encode()).decode()
    access_token = token.get("access_token")
    item.access_token_encrypted = f.encrypt(access_token.encode()).decode() if access_token else None
    item.expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(token.get("expires_in", 3600))) if access_token else None
    item.scope = token.get("scope", GOOGLE_SCOPE)
    db.commit()
    return {"connected": True, "provider": "google_drive", "message": "Google Drive connected. Return to Narrativ Forge."}

async def access_token_for(user_email: str, organization_id: str, db: Session):
    item = db.query(GoogleDriveConnection).filter(GoogleDriveConnection.user_email == user_email, GoogleDriveConnection.organization_id == organization_id).first()
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
