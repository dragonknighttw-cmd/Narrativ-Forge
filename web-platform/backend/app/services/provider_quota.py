from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models import Organization, UsageEvent


class ProviderQuotaExceeded(RuntimeError):
    pass


@dataclass(frozen=True)
class ProviderQuota:
    provider: str
    unit: str
    limit: int
    used: int
    remaining: int
    warning: bool
    fallback: bool


def _period_start(now: datetime | None = None) -> datetime:
    value = now or datetime.now(timezone.utc)
    return value.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


def _policy(provider: str) -> tuple[int, str]:
    normalized = provider.lower()
    if normalized == "agnes":
        return max(0, settings.agnes_daily_seconds_budget), "second"
    if normalized == "groq":
        return max(0, settings.groq_daily_requests_budget), "request"
    raise ValueError(f"Unsupported provider quota: {provider}")


def get_provider_quota(
    db: Session,
    organization_id: str,
    provider: str,
    *,
    now: datetime | None = None,
) -> ProviderQuota:
    limit, unit = _policy(provider)
    period = _period_start(now)
    metric = f"provider:{provider.lower()}"
    used = int(
        db.scalar(
            select(func.coalesce(func.sum(UsageEvent.quantity), 0)).where(
                UsageEvent.organization_id == organization_id,
                UsageEvent.metric == metric,
                UsageEvent.period_start == period,
            )
        )
        or 0
    )
    remaining = max(0, limit - used)
    ratio = (used / limit) if limit else 1.0
    return ProviderQuota(
        provider=provider.lower(),
        unit=unit,
        limit=limit,
        used=used,
        remaining=remaining,
        warning=ratio >= settings.provider_quota_warning_threshold,
        fallback=ratio >= settings.provider_quota_fallback_threshold,
    )


def reserve_provider_quota(
    db: Session,
    organization_id: str,
    provider: str,
    quantity: int,
    *,
    idempotency_key: str,
    now: datetime | None = None,
) -> ProviderQuota:
    if quantity <= 0:
        raise ValueError("quantity must be greater than zero")
    limit, unit = _policy(provider)
    period = _period_start(now)
    metric = f"provider:{provider.lower()}"

    existing = db.scalar(
        select(UsageEvent).where(UsageEvent.idempotency_key == idempotency_key)
    )
    if existing is not None:
        existing_period = existing.period_start
        if existing_period is not None and existing_period.tzinfo is None:
            existing_period = existing_period.replace(tzinfo=timezone.utc)
        if (
            existing.organization_id != organization_id
            or existing.metric != metric
            or existing_period != period
            or existing.unit != unit
            or existing.quantity != quantity
        ):
            raise ValueError("Idempotency key is already bound to a different provider quota reservation")
        return get_provider_quota(db, organization_id, provider, now=now)

    # Serialize reservations per organization on PostgreSQL. SQLite remains
    # covered by the normal transaction used by the caller.
    db.execute(
        select(Organization.id)
        .where(Organization.id == organization_id)
        .with_for_update()
    ).first()

    used = int(
        db.scalar(
            select(func.coalesce(func.sum(UsageEvent.quantity), 0)).where(
                UsageEvent.organization_id == organization_id,
                UsageEvent.metric == metric,
                UsageEvent.period_start == period,
            )
        )
        or 0
    )
    if used + quantity > limit:
        raise ProviderQuotaExceeded(
            f"{provider} quota exceeded: requested={quantity} used={used} limit={limit}"
        )

    db.add(
        UsageEvent(
            organization_id=organization_id,
            metric=metric,
            quantity=quantity,
            unit=unit,
            idempotency_key=idempotency_key,
            period_start=period,
            metadata_json=json.dumps(
                {"provider": provider.lower(), "quantity": quantity},
                separators=(",", ":"),
            ),
        )
    )
    db.flush()
    return get_provider_quota(db, organization_id, provider, now=now)
