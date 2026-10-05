from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, require_roles, issue_session
from ...db import get_db
from ...workers.celery_app import get_celery
from ...models import (
    BillingSubscription, Invitation, MagicLinkToken, Organization,
    OrganizationMembership, Tag, TagAssignment, UsageEvent, WebhookEndpoint, NotificationEvent,
)
from ...services.passwords import hash_password
from ...core.config import settings

router = APIRouter(prefix="/phase4", tags=["phase4"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:100] or "workspace"


def ensure_membership(db: Session, user: dict) -> OrganizationMembership:
    membership = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.user_id == user["id"])
        .order_by(OrganizationMembership.created_at)
        .first()
    )
    if membership:
        return membership
    base = _slug(user["email"].split("@", 1)[0])
    slug = base
    suffix = 1
    while db.query(Organization).filter(Organization.slug == slug).first():
        suffix += 1
        slug = f"{base}-{suffix}"
    org = Organization(name=f"{user['email']}'s Workspace", slug=slug, plan="trial")
    db.add(org)
    db.flush()
    membership = OrganizationMembership(organization_id=org.id, user_id=user["id"], role=user["role"])
    db.add(membership)
    db.add(BillingSubscription(organization_id=org.id, plan="trial", status="trialing"))
    db.commit()
    db.refresh(membership)
    return membership


def current_membership(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return ensure_membership(db, user)


class InviteCreate(BaseModel):
    email: str
    role: str = "viewer"

    @field_validator("email")
    @classmethod
    def email_value(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
            raise ValueError("Invalid email")
        return value


class InviteAccept(BaseModel):
    token: str
    password: str


class MagicLinkRequest(BaseModel):
    email: str


class MagicLinkConsume(BaseModel):
    token: str


class TagCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 80:
            raise ValueError("Invalid tag name")
        return value


class TagAssign(BaseModel):
    resource_type: str
    resource_id: str


class UsageRecord(BaseModel):
    metric: str
    quantity: int = 1
    unit: str = "unit"
    idempotency_key: str | None = None
    metadata: dict = {}


@router.get("/workspace")
def workspace(membership=Depends(current_membership), db: Session = Depends(get_db)):
    org = db.get(Organization, membership.organization_id)
    return {"id": org.id, "name": org.name, "slug": org.slug, "plan": org.plan, "role": membership.role}


@router.post("/invitations")
def create_invitation(
    payload: InviteCreate,
    membership=Depends(current_membership),
    user=Depends(require_roles("owner")),
    db: Session = Depends(get_db),
):
    if payload.role not in {"owner", "editor", "viewer"}:
        raise HTTPException(status_code=422, detail="Invalid role")
    token = secrets.token_urlsafe(32)
    invitation = Invitation(
        organization_id=membership.organization_id,
        email=payload.email,
        role=payload.role,
        token_hash=_token_hash(token),
        expires_at=_now() + timedelta(days=7),
    )
    db.add(invitation)
    db.commit()
    return {
        "id": invitation.id,
        "email": invitation.email,
        "role": invitation.role,
        "expires_at": invitation.expires_at,
        "delivery": "pending",
        "token": token,
    }


@router.post("/invitations/accept")
def accept_invitation(payload: InviteAccept, response: Response, db: Session = Depends(get_db)):
    invitation = db.query(Invitation).filter(
        Invitation.token_hash == _token_hash(payload.token),
        Invitation.status == "pending",
        Invitation.expires_at > _now(),
    ).first()
    if not invitation:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    from ...models import User
    user = db.query(User).filter(User.email == invitation.email).first()
    if not user:
        try:
            password_hash = hash_password(payload.password)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        user = User(email=invitation.email, role=invitation.role, password_hash=password_hash, is_active=True)
        db.add(user)
        db.flush()
    if not db.query(OrganizationMembership).filter_by(
        organization_id=invitation.organization_id, user_id=user.id
    ).first():
        db.add(OrganizationMembership(
            organization_id=invitation.organization_id, user_id=user.id, role=invitation.role
        ))
    invitation.status = "accepted"
    invitation.accepted_at = _now()
    db.commit()
    response.set_cookie(
        key=settings.session_cookie_name, value=issue_session(user.email, user.role),
        httponly=True, secure=settings.session_cookie_secure, samesite="strict", max_age=settings.session_ttl_seconds, path="/",
    )
    return {"authenticated": True, "user": {"id": user.id, "email": user.email, "role": user.role}}


@router.post("/magic-link/request")
def request_magic_link(payload: MagicLinkRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    from ...models import User
    user = db.query(User).filter(User.email == email, User.is_active.is_(True)).first()
    if not user:
        return {"requested": True}
    token = secrets.token_urlsafe(32)
    db.query(MagicLinkToken).filter(
        MagicLinkToken.email == email, MagicLinkToken.consumed_at.is_(None)
    ).update({"consumed_at": _now()})
    db.add(MagicLinkToken(email=email, token_hash=_token_hash(token), expires_at=_now() + timedelta(minutes=15)))
    db.commit()
    return {"requested": True, "delivery": "pending", "token": token}


@router.post("/magic-link/consume")
def consume_magic_link(payload: MagicLinkConsume, response: Response, db: Session = Depends(get_db)):
    record = db.query(MagicLinkToken).filter(
        MagicLinkToken.token_hash == _token_hash(payload.token),
        MagicLinkToken.consumed_at.is_(None),
        MagicLinkToken.expires_at > _now(),
    ).first()
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired magic link")
    from ...models import User
    user = db.query(User).filter(User.email == record.email, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Account not found")
    record.consumed_at = _now()
    db.commit()
    response.set_cookie(
        key="nf_session", value=issue_session(user.email, user.role),
        httponly=True, secure=False, samesite="strict", max_age=8 * 3600, path="/",
    )
    return {"authenticated": True, "user": {"id": user.id, "email": user.email, "role": user.role}}


@router.get("/tags")
def list_tags(membership=Depends(current_membership), db: Session = Depends(get_db)):
    return db.query(Tag).filter(Tag.organization_id == membership.organization_id).order_by(Tag.name).all()


@router.post("/tags")
def create_tag(payload: TagCreate, membership=Depends(current_membership), db: Session = Depends(get_db)):
    slug = _slug(payload.name)
    tag = Tag(organization_id=membership.organization_id, name=payload.name, slug=slug)
    db.add(tag)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Tag already exists") from exc
    db.refresh(tag)
    return tag


@router.post("/tags/{tag_id}/assign")
def assign_tag(tag_id: str, payload: TagAssign, membership=Depends(current_membership), db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id, Tag.organization_id == membership.organization_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    assignment = TagAssignment(tag_id=tag.id, resource_type=payload.resource_type, resource_id=payload.resource_id)
    db.add(assignment)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        assignment = db.query(TagAssignment).filter_by(
            tag_id=tag.id, resource_type=payload.resource_type, resource_id=payload.resource_id
        ).first()
    return assignment


@router.get("/tags/{tag_id}/assignments")
def list_tag_assignments(tag_id: str, membership=Depends(current_membership), db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == tag_id, Tag.organization_id == membership.organization_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db.query(TagAssignment).filter(TagAssignment.tag_id == tag.id).all()


@router.post("/usage")
def record_usage(payload: UsageRecord, membership=Depends(current_membership), db: Session = Depends(get_db)):
    if payload.quantity <= 0 or len(payload.metric.strip()) > 80:
        raise HTTPException(status_code=422, detail="Invalid usage")
    period = _now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if payload.idempotency_key:
        existing = db.query(UsageEvent).filter(UsageEvent.idempotency_key == payload.idempotency_key).first()
        if existing:
            return existing
    event = UsageEvent(
        organization_id=membership.organization_id, metric=payload.metric.strip(),
        quantity=payload.quantity, unit=payload.unit, idempotency_key=payload.idempotency_key,
        period_start=period, metadata_json=json.dumps(payload.metadata, separators=(",", ":")),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/usage")
def usage(membership=Depends(current_membership), db: Session = Depends(get_db)):
    period = _now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    rows = db.query(UsageEvent).filter(
        UsageEvent.organization_id == membership.organization_id, UsageEvent.period_start == period
    ).all()
    totals = {}
    for row in rows:
        totals[row.metric] = totals.get(row.metric, 0) + row.quantity
    return {"period_start": period, "totals": totals}


@router.get("/billing")
def billing(membership=Depends(current_membership), db: Session = Depends(get_db)):
    sub = db.query(BillingSubscription).filter(BillingSubscription.organization_id == membership.organization_id).first()
    return sub


@router.post("/billing/plan")
def set_plan(plan: str, membership=Depends(current_membership), user=Depends(require_roles("owner")), db: Session = Depends(get_db)):
    allowed = {"trial", "free", "pro", "business"}
    if plan not in allowed:
        raise HTTPException(status_code=422, detail="Invalid plan")
    sub = db.query(BillingSubscription).filter(BillingSubscription.organization_id == membership.organization_id).first()
    sub.plan = plan
    sub.status = "active" if plan != "trial" else "trialing"
    org = db.get(Organization, membership.organization_id)
    org.plan = plan
    db.commit()
    return sub


class WebhookCreate(BaseModel):
    url: str
    events: list[str] = []

class NotificationCreate(BaseModel):
    event_type: str
    payload: dict = {}

@router.post("/webhooks")
def create_webhook(payload: WebhookCreate, membership=Depends(current_membership), db: Session = Depends(get_db)):
    secret = secrets.token_urlsafe(32)
    endpoint = WebhookEndpoint(
        organization_id=membership.organization_id,
        url=payload.url.strip(),
        secret_hash=_token_hash(secret),
        events_json=json.dumps(payload.events),
    )
    db.add(endpoint)
    db.commit()
    db.refresh(endpoint)
    return {"id": endpoint.id, "url": endpoint.url, "events": payload.events, "secret": secret}

@router.get("/webhooks")
def list_webhooks(membership=Depends(current_membership), db: Session = Depends(get_db)):
    rows = db.query(WebhookEndpoint).filter(WebhookEndpoint.organization_id == membership.organization_id).all()
    return [{"id": r.id, "url": r.url, "events": json.loads(r.events_json or "[]"), "is_active": r.is_active, "created_at": r.created_at} for r in rows]

@router.delete("/webhooks/{webhook_id}")
def delete_webhook(webhook_id: str, membership=Depends(current_membership), user=Depends(require_roles("owner")), db: Session = Depends(get_db)):
    row = db.query(WebhookEndpoint).filter(WebhookEndpoint.id == webhook_id, WebhookEndpoint.organization_id == membership.organization_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Webhook not found")
    row.is_active = False
    db.commit()
    return {"id": row.id, "is_active": False}

@router.post("/notifications")
def create_notification(payload: NotificationCreate, membership=Depends(current_membership), db: Session = Depends(get_db)):
    event = NotificationEvent(
        organization_id=membership.organization_id,
        event_type=payload.event_type,
        payload_json=json.dumps(payload.payload, separators=(",", ":")),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    try:
        get_celery().send_task("narrativ.deliver_notification", args=[event.id])
    except Exception:
        pass
    return {"id": event.id, "status": event.status}

@router.get("/notifications")
def list_notifications(membership=Depends(current_membership), db: Session = Depends(get_db)):
    rows = db.query(NotificationEvent).filter(
        NotificationEvent.organization_id == membership.organization_id
    ).order_by(NotificationEvent.created_at.desc()).limit(100).all()
    return rows
