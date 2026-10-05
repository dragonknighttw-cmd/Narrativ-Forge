from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Response, Request
from pydantic import BaseModel, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, require_roles, issue_session
from ...db import get_db
from ...workers.celery_app import get_celery
from ...models import (
    BillingSubscription, Invitation, MagicLinkToken, Organization,
    OrganizationMembership, Tag, TagAssignment, UsageEvent, WebhookEndpoint, NotificationEvent, StripeWebhookEvent,
)
from ...services.passwords import hash_password
from ...core.config import settings
from cryptography.fernet import Fernet

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

def _resource_belongs_to_org(db: Session, organization_id: str, resource_type: str, resource_id: str) -> bool:
    from ...models import Idea, Series, Episode, ManualProductionLog, SocialPublication
    resource_type = resource_type.strip().lower()
    if resource_type == "idea":
        return db.query(Idea.id).filter(Idea.id == resource_id, Idea.organization_id == organization_id).first() is not None
    if resource_type == "series":
        return db.query(Series.id).filter(Series.id == resource_id, Series.organization_id == organization_id).first() is not None
    if resource_type == "episode":
        return db.query(Episode.id).filter(Episode.id == resource_id, Episode.organization_id == organization_id).first() is not None
    if resource_type == "production_log":
        return db.query(ManualProductionLog.id).join(Episode, ManualProductionLog.episode_id == Episode.id).filter(
            ManualProductionLog.id == resource_id, Episode.organization_id == organization_id
        ).first() is not None
    if resource_type == "social_publication":
        return db.query(SocialPublication.id).join(Episode, SocialPublication.episode_id == Episode.id).filter(
            SocialPublication.id == resource_id, Episode.organization_id == organization_id
        ).first() is not None
    raise HTTPException(status_code=422, detail="Unsupported tag resource type")



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
    try:
        get_celery().send_task("narrativ.send_email", args=[payload.email, "You are invited to Narrativ Forge", f"Accept your workspace invitation: {settings.frontend_base_url}/invite?token={token}"])
        delivery = "queued"
    except Exception:
        delivery = "pending"
    return {
        "id": invitation.id,
        "email": invitation.email,
        "role": invitation.role,
        "expires_at": invitation.expires_at,
        "delivery": delivery,
        "token": None if settings.is_production else token,
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
    existing_membership = db.query(OrganizationMembership).filter_by(organization_id=invitation.organization_id, user_id=user.id).first()
    if not existing_membership:
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
    try:
        get_celery().send_task("narrativ.send_email", args=[email, "Your Narrativ Forge sign-in link", f"Sign in to Narrativ Forge: {settings.frontend_base_url}/auth/magic-link?token={token}"])
        delivery = "queued"
    except Exception:
        delivery = "pending"
    return {"requested": True, "delivery": delivery, "token": None if settings.is_production else token}


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
        key=settings.session_cookie_name, value=issue_session(user.email, user.role),
        httponly=True, secure=settings.session_cookie_secure, samesite="strict", max_age=settings.session_ttl_seconds, path="/",
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
    if not _resource_belongs_to_org(db, membership.organization_id, payload.resource_type, payload.resource_id):
        raise HTTPException(status_code=404, detail="Tag resource not found in workspace")
    assignment = TagAssignment(tag_id=tag.id, resource_type=payload.resource_type.strip().lower(), resource_id=payload.resource_id)
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

    @field_validator("url")
    @classmethod
    def webhook_url(cls, value: str) -> str:
        value = value.strip()
        parsed = urlparse(value)
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or not host:
            raise ValueError("Webhook URL must use HTTPS")
        if host in {"localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal", "169.254.169.254"}:
            raise ValueError("Webhook URL host is not allowed")
        return value

class NotificationCreate(BaseModel):
    event_type: str
    payload: dict = {}

@router.post("/webhooks")
def create_webhook(payload: WebhookCreate, membership=Depends(current_membership), db: Session = Depends(get_db)):
    secret = secrets.token_urlsafe(32)
    if not settings.oauth_encryption_key:
        raise HTTPException(status_code=503, detail="Webhook secret encryption is not configured")
    endpoint = WebhookEndpoint(
        organization_id=membership.organization_id,
        url=payload.url.strip(),
        secret_hash=_token_hash(secret),
        secret_encrypted=Fernet(settings.oauth_encryption_key.encode()).encrypt(secret.encode()).decode() if settings.oauth_encryption_key else None,
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


@router.post("/billing/checkout")
def create_checkout(plan: str, membership=Depends(current_membership), user=Depends(require_roles("owner")), db: Session = Depends(get_db)):
    if plan not in {"pro", "business"}:
        raise HTTPException(status_code=422, detail="Only paid plans can use Stripe Checkout")
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe billing is not configured")
    price_id = settings.stripe_price_pro if plan == "pro" else settings.stripe_price_business
    if not price_id:
        raise HTTPException(status_code=503, detail=f"Stripe price is not configured for {plan}")
    import stripe
    stripe.api_key = settings.stripe_secret_key
    sub = db.query(BillingSubscription).filter(BillingSubscription.organization_id == membership.organization_id).first()
    if not sub:
        sub = BillingSubscription(organization_id=membership.organization_id)
        db.add(sub)
        db.flush()
    if sub.external_subscription_id and sub.status in {"active", "trialing", "past_due", "incomplete"}:
        raise HTTPException(status_code=409, detail="Workspace already has an active Stripe subscription")
    if not sub.external_customer_id:
        customer = stripe.Customer.create(email=user["email"], metadata={"organization_id": membership.organization_id})
        sub.external_customer_id = customer.id
        sub.provider = "stripe"
        db.commit()
    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=sub.external_customer_id,
        client_reference_id=membership.organization_id,
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.frontend_base_url}/settings/billing?checkout=success",
        cancel_url=f"{settings.frontend_base_url}/settings/billing?checkout=cancelled",
        metadata={"organization_id": membership.organization_id, "plan": plan},
        subscription_data={"metadata": {"organization_id": membership.organization_id, "plan": plan}},
    )
    return {"id": session.id, "url": session.url, "plan": plan}

@router.post("/billing/portal")
def create_billing_portal(membership=Depends(current_membership), user=Depends(require_roles("owner")), db: Session = Depends(get_db)):
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe billing is not configured")
    sub = db.query(BillingSubscription).filter(BillingSubscription.organization_id == membership.organization_id).first()
    if not sub or not sub.external_customer_id:
        raise HTTPException(status_code=409, detail="Stripe customer is not provisioned")
    import stripe
    stripe.api_key = settings.stripe_secret_key
    session = stripe.billing_portal.Session.create(
        customer=sub.external_customer_id,
        return_url=f"{settings.frontend_base_url}/settings/billing",
    )
    return {"url": session.url}


def _stripe_plan(obj: dict) -> str | None:
    metadata = obj.get("metadata") or {}
    if metadata.get("plan") in {"pro", "business"}:
        return metadata["plan"]
    price_ids = {settings.stripe_price_pro: "pro", settings.stripe_price_business: "business"}
    items = ((obj.get("items") or {}).get("data") or [])
    for item in items:
        price_id = ((item.get("price") or {}).get("id"))
        if price_id in price_ids:
            return price_ids[price_id]
    return None

@router.post("/billing/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook is not configured")
    try:
        import stripe
        payload = await request.body()
        signature = request.headers.get("stripe-signature", "")
        event = stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook") from exc

    event_id = event.get("id")
    if not event_id:
        raise HTTPException(status_code=400, detail="Stripe webhook event id is missing")
    if db.get(StripeWebhookEvent, event_id):
        return {"received": True, "duplicate": True}

    event_type = event["type"]
    obj = event["data"]["object"]
    customer_id = obj.get("customer")
    if event_type == "checkout.session.completed":
        customer_id = obj.get("customer")
    sub_id = obj.get("id") if event_type.startswith("customer.subscription.") else obj.get("subscription")
    sub = db.query(BillingSubscription).filter(
        BillingSubscription.external_customer_id == customer_id
    ).first() if customer_id else None

    if sub:
        sub.provider = "stripe"
        if sub_id:
            sub.external_subscription_id = sub_id
        if event_type == "checkout.session.completed":
            plan = _stripe_plan(obj)
            if plan:
                sub.plan = plan
        elif event_type.startswith("customer.subscription."):
            metadata = obj.get("metadata") or {}
            plan = metadata.get("plan")
            if plan in {"pro", "business"}:
                sub.plan = plan
            sub.status = "canceled" if event_type == "customer.subscription.deleted" else obj.get("status", sub.status)
            if obj.get("current_period_start"):
                sub.current_period_start = datetime.fromtimestamp(obj["current_period_start"], tz=timezone.utc)
            if obj.get("current_period_end"):
                sub.current_period_end = datetime.fromtimestamp(obj["current_period_end"], tz=timezone.utc)
        elif event_type == "invoice.payment_failed":
            sub.status = "past_due"
        elif event_type == "invoice.paid":
            if sub.status in {"past_due", "incomplete"}:
                sub.status = "active"

        org = db.get(Organization, sub.organization_id)
        if org:
            org.plan = "free" if sub.status == "canceled" else sub.plan
        db.commit()

    db.add(StripeWebhookEvent(id=event_id, event_type=event_type))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"received": True, "duplicate": True}
    return {"received": True}
