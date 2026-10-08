import base64
import hashlib
import hmac
import time

from fastapi import Cookie, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import OrganizationMembership, User

from ..core.config import settings


def _sign_session(email: str, role: str = "owner", organization_id: str | None = None) -> str:
    expires_at = int(time.time()) + settings.session_ttl_seconds
    payload = (
        f"v2|{email}|{role}|{organization_id}|{expires_at}"
        if organization_id
        else f"v1|{email}|{role}|{expires_at}"
    )
    signature = hmac.new(settings.session_secret.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(f"{payload}|{signature.hex()}".encode()).decode().rstrip("=")


def verify_session(value: str) -> dict:
    try:
        padded = value + "=" * (-len(value) % 4)
        raw = base64.urlsafe_b64decode(padded.encode()).decode()
        parts = raw.split("|")
        if len(parts) == 5:
            version, email, role, expires_at, signature = parts
            organization_id = None
        elif len(parts) == 6:
            version, email, role, organization_id, expires_at, signature = parts
        else:
            raise ValueError("invalid session")
        if version not in {"v1", "v2"} or not email or role not in {"owner", "editor", "viewer"}:
            raise ValueError("invalid session")
        if version == "v2" and not organization_id:
            raise ValueError("invalid session")
        if int(expires_at) < int(time.time()):
            raise ValueError("expired session")
        payload = "|".join(parts[:-1])
        expected = hmac.new(settings.session_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("invalid signature")
        return {"id": email, "email": email, "role": role, "organization_id": organization_id}
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
    membership_query = db.query(OrganizationMembership).filter(OrganizationMembership.user_id == db_user.id)
    if session_user.get("organization_id"):
        membership_query = membership_query.filter(OrganizationMembership.organization_id == session_user["organization_id"])
    membership = membership_query.order_by(OrganizationMembership.created_at).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Workspace membership required")
    return {"id": db_user.id, "email": db_user.email, "role": membership.role, "organization_id": membership.organization_id}


def require_roles(*roles: str):
    def dependency(user=Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return dependency


def get_current_membership(user=Depends(get_current_user), db: Session = Depends(get_db)):
    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.user_id == user["id"],
            OrganizationMembership.organization_id == user["organization_id"],
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Workspace membership required")
    return membership
