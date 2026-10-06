from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, field_validator
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import re
from sqlalchemy.orm import Session

from ..dependencies import get_current_membership, get_current_user, issue_session, require_roles
from ...core.config import settings
from ...db import get_db
from ...models import MagicLinkToken, OrganizationMembership, User
from ...services.passwords import hash_password, verify_password
from ...services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Invalid email")
        return value


class InviteRequest(BaseModel):
    email: str
    password: str
    role: str = "viewer"

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Invalid email")
        return value


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    if settings.single_user_mode and payload.email.lower() != settings.single_user_email.strip().lower():
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = db.query(User).filter(User.email == payload.email.lower(), User.is_active.is_(True)).first()
    if not user:
        # Keep the same response for unknown users and bad passwords.
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    response.set_cookie(
        key=settings.session_cookie_name,
        value=issue_session(user.email, user.role),
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="strict",
        max_age=settings.session_ttl_seconds,
        path="/",
    )
    return {"authenticated": True, "user": {"id": user.id, "email": user.email, "role": user.role}}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=settings.session_cookie_name, path="/")
    return {"authenticated": False}


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user


@router.post("/invite")
def invite(
    payload: InviteRequest,
    user=Depends(require_roles("owner")),
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    if settings.single_user_mode:
        raise HTTPException(status_code=403, detail="Invitations are disabled in single-user mode")
    role = payload.role.lower()
    if role not in {"owner", "editor", "viewer"}:
        raise HTTPException(status_code=422, detail="Invalid role")
    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="User already exists")
    try:
        password_hash = hash_password(payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    created = User(email=email, role=role, password_hash=password_hash, is_active=True)
    db.add(created)
    db.flush()
    db.add(OrganizationMembership(organization_id=membership.organization_id, user_id=created.id, role=role))
    db.commit()
    db.refresh(created)
    return {"id": created.id, "email": created.email, "role": created.role}


@router.get("/users")
def users(
    user=Depends(require_roles("owner")),
    db: Session = Depends(get_db),
):
    return [
        {"id": item.id, "email": item.email, "role": item.role, "is_active": item.is_active}
        for item in db.query(User).order_by(User.email).all()
    ]


class MagicLinkRequest(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Invalid email")
        return value


@router.post("/magic-link/request")
def request_magic_link(payload: MagicLinkRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email, User.is_active.is_(True)).first()
    if not user:
        return {"accepted": True}

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    token = MagicLinkToken(
        email=user.email,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    )
    db.add(token)
    db.commit()

    link = settings.frontend_base_url.rstrip("/") + "/auth/magic-link?token=" + raw_token
    try:
        send_email(
            recipient=user.email,
            subject="Narrativ Forge magic link",
            body="Open this link to sign in to Narrativ Forge:\n\n" + link + "\n\nThis link expires in 15 minutes.",
        )
    except Exception:
        db.delete(token)
        db.commit()
        raise HTTPException(status_code=503, detail="Magic-link email delivery is unavailable")
    return {"accepted": True}


@router.post("/magic-link/consume")
def consume_magic_link(token: str, response: Response, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    record = (
        db.query(MagicLinkToken)
        .filter(
            MagicLinkToken.token_hash == token_hash,
            MagicLinkToken.consumed_at.is_(None),
        )
        .first()
    )
    if not record or record.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Magic link is invalid or expired")

    user = db.query(User).filter(User.email == record.email, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Magic link is invalid or expired")

    record.consumed_at = datetime.now(timezone.utc)
    db.commit()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=issue_session(user.email, user.role),
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="strict",
        max_age=settings.session_ttl_seconds,
        path="/",
    )
    return {"authenticated": True, "user": {"id": user.id, "email": user.email, "role": user.role}}
