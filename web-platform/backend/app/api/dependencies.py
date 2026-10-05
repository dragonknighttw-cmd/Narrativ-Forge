import base64
import hashlib
import hmac
import time

from fastapi import Cookie, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User

from ..core.config import settings


def _sign_session(email: str, role: str = "owner") -> str:
    expires_at = int(time.time()) + settings.session_ttl_seconds
    payload = f"v1|{email}|{role}|{expires_at}"
    signature = hmac.new(settings.session_secret.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(f"{payload}|{signature.hex()}".encode()).decode().rstrip("=")


def verify_session(value: str) -> dict:
    try:
        padded = value + "=" * (-len(value) % 4)
        raw = base64.urlsafe_b64decode(padded.encode()).decode()
        version, email, role, expires_at, signature = raw.split("|", 4)
        if version != "v1" or not email or role not in {"owner", "editor", "viewer"}:
            raise ValueError("invalid session")
        if int(expires_at) < int(time.time()):
            raise ValueError("expired session")
        payload = f"{version}|{email}|{role}|{expires_at}"
        expected = hmac.new(settings.session_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid signature")
        return {"id": email, "email": email, "role": role}
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Authentication required") from exc


def issue_session(email: str, role: str = "owner") -> str:
    return _sign_session(email, role)


def get_current_user(
    session_cookie: str | None = Cookie(default=None, alias=settings.session_cookie_name),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    value = session_cookie
    if not value and authorization and authorization.startswith("Bearer "):
        value = authorization.removeprefix("Bearer ").strip()
    if not value:
        raise HTTPException(status_code=401, detail="Authentication required")
    session_user = verify_session(value)
    db_user = db.query(User).filter(User.email == session_user["email"], User.is_active.is_(True)).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return {"id": db_user.id, "email": db_user.email, "role": db_user.role}


def require_roles(*roles: str):
    def dependency(user=Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return dependency
\n\ndef get_current_membership(user=Depends(get_current_user), db: Session = Depends(get_db)):\n    membership = (\n        db.query(OrganizationMembership)\n        .filter(OrganizationMembership.user_id == user["id"])\n        .order_by(OrganizationMembership.created_at)\n        .first()\n    )\n    if not membership:\n        raise HTTPException(status_code=403, detail="Workspace membership required")\n    return membership\n