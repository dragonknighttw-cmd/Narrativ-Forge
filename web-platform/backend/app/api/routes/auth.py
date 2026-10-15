from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, field_validator
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
import re
import requests
from sqlalchemy.orm import Session

from ..dependencies import get_current_membership, get_current_user, issue_session, require_roles
from ...core.config import settings
from ...db import get_db
from ...models import MagicLinkToken, Organization, OrganizationMembership, User
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


class SupabaseLoginRequest(BaseModel):
    access_token: str

    @field_validator("access_token")
    @classmethod
    def valid_access_token(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 8192:
            raise ValueError("Invalid access token")
        return value


@router.post("/supabase-login")
def supabase_login(payload: SupabaseLoginRequest, response: Response, db: Session = Depends(get_db)):
    """Validate a Supabase Auth access token and map it to a workspace session.

    Only the configured Supabase user may be auto-provisioned as the first Owner.
    Other users must already have a local user + organization membership created
    by the invitation acceptance flow.
    """
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(status_code=503, detail="Supabase Auth is not configured")
    if not settings.supabase_owner_user_id or not settings.supabase_owner_email:
        raise HTTPException(status_code=503, detail="Initial Owner identity is not configured")

    try:
        auth_response = requests.get(
            settings.supabase_url.rstrip("/") + "/auth/v1/user",
            headers={
                "apikey": settings.supabase_anon_key,
                "Authorization": "Bearer " + payload.access_token,
            },
            timeout=8,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail="Supabase Auth is temporarily unavailable") from exc
    if auth_response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired Supabase session")
    try:
        identity = auth_response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="Invalid response from Supabase Auth") from exc

    user_id = str(identity.get("id") or "")
    email = str(identity.get("email") or "").strip().lower()
    if not user_id or not email or not identity.get("email_confirmed_at"):
        raise HTTPException(status_code=403, detail="A confirmed Supabase email is required")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        # The first user is allowed only by immutable server-side UUID + email config.
        if user_id != settings.supabase_owner_user_id or email != settings.supabase_owner_email.strip().lower():
            raise HTTPException(status_code=403, detail="Workspace membership required")
        email_conflict = db.query(User).filter(User.email == email).first()
        if email_conflict is not None:
            raise HTTPException(status_code=409, detail="Account mapping conflict; contact the workspace owner")
        organization = db.query(Organization).filter(
            Organization.slug == settings.supabase_owner_organization_slug
        ).first()
        if organization is None:
            raise HTTPException(status_code=503, detail="Configured Owner workspace was not found")
        user = User(
            id=user_id, email=email, role="owner", password_hash="supabase-auth-managed", is_active=True
        )
        try:
            db.add(user)
            db.flush()
            membership = OrganizationMembership(
                organization_id=organization.id, user_id=user.id, role="owner"
            )
            db.add(membership)
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            raise HTTPException(status_code=409, detail="Owner account could not be provisioned safely")
    else:
        if user.email.strip().lower() != email or not user.is_active:
            raise HTTPException(status_code=403, detail="Account is not active")
        membership = (
            db.query(OrganizationMembership)
            .filter(OrganizationMembership.user_id == user.id)
            .order_by(OrganizationMembership.created_at)
            .first()
        )
        if membership is None:
            raise HTTPException(status_code=403, detail="Workspace membership required")
        if user_id == settings.supabase_owner_user_id and email == settings.supabase_owner_email.strip().lower():
            # The exact configured Owner identity is authoritative, never user-editable metadata.
            user.role = "owner"
            membership.role = "owner"
            db.commit()

    membership = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.user_id == user.id)
        .order_by(OrganizationMembership.created_at)
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=403, detail="Workspace membership required")
    response.set_cookie(
        key=settings.session_cookie_name,
        value=issue_session(user.email, membership.role, membership.organization_id),
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="strict",
        max_age=settings.session_ttl_seconds,
        path="/",
    )
    return {"authenticated": True, "user": {
        "id": user.id, "email": user.email, "role": membership.role,
        "organization_id": membership.organization_id,
    }}


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
    if settings.is_production:
        raise HTTPException(status_code=410, detail="Password login is managed by Supabase Auth")
    if settings.single_user_mode and payload.email.lower() != settings.single_user_email.strip().lower():
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user = db.query(User).filter(User.email == payload.email.lower(), User.is_active.is_(True)).first()
    if not user:
        # Keep the same response for unknown users and bad passwords.
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    membership = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.user_id == user.id)
        .order_by(OrganizationMembership.created_at)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Workspace membership required")
    response.set_cookie(
        key=settings.session_cookie_name,
        value=issue_session(user.email, membership.role, membership.organization_id),
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="strict",
        max_age=settings.session_ttl_seconds,
        path="/",
    )
    return {"authenticated": True, "user": {"id": user.id, "email": user.email, "role": membership.role, "organization_id": membership.organization_id}}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=settings.session_cookie_name, path="/")
    return {"authenticated": False}


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user


class WorkspaceSwitchRequest(BaseModel):
    organization_id: str


@router.post("/switch-workspace")
def switch_workspace(
    payload: WorkspaceSwitchRequest,
    response: Response,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.user_id == user["id"],
            OrganizationMembership.organization_id == payload.organization_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Workspace membership not found")
    response.set_cookie(
        key=settings.session_cookie_name,
        value=issue_session(user["email"], membership.role, membership.organization_id),
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="strict",
        max_age=settings.session_ttl_seconds,
        path="/",
    )
    return {"authenticated": True, "organization_id": membership.organization_id, "role": membership.role}


@router.post("/invite")
def invite(
    payload: InviteRequest,
    user=Depends(require_roles("owner")),
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    if settings.is_production:
        raise HTTPException(status_code=410, detail="Use Supabase-backed workspace invitations")
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
    membership=Depends(get_current_membership),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(User, OrganizationMembership.role)
        .join(OrganizationMembership, OrganizationMembership.user_id == User.id)
        .filter(OrganizationMembership.organization_id == membership.organization_id)
        .order_by(User.email)
        .all()
    )
    return [
        {"id": item.id, "email": item.email, "role": org_role, "is_active": item.is_active}
        for item, org_role in rows
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
    if settings.is_production:
        raise HTTPException(status_code=410, detail="Use Supabase Auth for sign-in links")
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
    if settings.is_production:
        raise HTTPException(status_code=410, detail="Use Supabase Auth for sign-in links")
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    record = (
        db.query(MagicLinkToken)
        .filter(
            MagicLinkToken.token_hash == token_hash,
            MagicLinkToken.consumed_at.is_(None),
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=401, detail="Magic link is invalid or expired")
    expires_at = record.expires_at
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at is None or expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Magic link is invalid or expired")

    user = db.query(User).filter(User.email == record.email, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Magic link is invalid or expired")

    membership = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.user_id == user.id)
        .order_by(OrganizationMembership.created_at)
        .first()
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Workspace membership required")

    record.consumed_at = datetime.now(timezone.utc)
    db.commit()
    response.set_cookie(
        key=settings.session_cookie_name,
        value=issue_session(user.email, membership.role, membership.organization_id),
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="strict",
        max_age=settings.session_ttl_seconds,
        path="/",
    )
    return {"authenticated": True, "user": {"id": user.id, "email": user.email, "role": membership.role, "organization_id": membership.organization_id}}
