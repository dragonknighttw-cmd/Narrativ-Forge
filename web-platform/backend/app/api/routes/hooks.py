from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import HookLibrary, OrganizationMembership
from ..dependencies import get_current_user, require_roles

router = APIRouter(prefix="/hooks", tags=["hooks"])

def membership_for(user, db):
    return db.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user["id"]
    ).order_by(OrganizationMembership.created_at).first()

class HookCreate(BaseModel):
    hook_text: str
    hook_type: str = "general"
    topic: str | None = None
    emotion: str | None = None

    @field_validator("hook_text")
    @classmethod
    def text_valid(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 4000:
            raise ValueError("Hook text must be 1-4000 characters")
        return value

@router.get("")
def list_hooks(
    q: str | None = None,
    hook_type: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = membership_for(user, db)
    query = db.query(HookLibrary).filter(
        (HookLibrary.organization_id == (membership.organization_id if membership else None)) |
        (HookLibrary.is_default.is_(True))
    )
    if q:
        query = query.filter(HookLibrary.hook_text.ilike(f"%{q.strip()}%"))
    if hook_type:
        query = query.filter(HookLibrary.hook_type == hook_type)
    return query.order_by(HookLibrary.performance_score.desc().nullslast(), HookLibrary.created_at.desc()).limit(limit).all()

@router.post("")
def create_hook(
    payload: HookCreate,
    user=Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    membership = membership_for(user, db)
    if not membership:
        raise HTTPException(status_code=403, detail="Workspace membership required")
    hook = HookLibrary(
        organization_id=membership.organization_id,
        hook_text=payload.hook_text,
        hook_type=payload.hook_type.strip()[:40] or "general",
        topic=payload.topic.strip()[:100] if payload.topic else None,
        emotion=payload.emotion.strip()[:100] if payload.emotion else None,
    )
    db.add(hook)
    db.commit()
    db.refresh(hook)
    return hook

@router.patch("/{hook_id}/performance")
def update_hook_performance(
    hook_id: str,
    views_average: float | None = None,
    completion_average: float | None = None,
    shares_average: float | None = None,
    performance_score: float | None = None,
    user=Depends(require_roles("owner", "editor")),
    db: Session = Depends(get_db),
):
    membership = membership_for(user, db)
    hook = db.query(HookLibrary).filter(
        HookLibrary.id == hook_id,
        HookLibrary.organization_id == membership.organization_id,
    ).first()
    if not hook:
        raise HTTPException(status_code=404, detail="Hook not found")
    if views_average is not None:
        hook.views_average = max(0, views_average)
    if completion_average is not None:
        hook.completion_average = max(0, completion_average)
    if shares_average is not None:
        hook.shares_average = max(0, shares_average)
    if performance_score is not None:
        hook.performance_score = performance_score
    hook.used_count += 1
    db.commit()
    return hook
