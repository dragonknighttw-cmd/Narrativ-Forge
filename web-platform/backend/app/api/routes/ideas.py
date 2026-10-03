from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Idea
from ..dependencies import get_current_user, require_roles

router = APIRouter(prefix="/ideas", tags=["ideas"])


def validate_idea_gate(concept: str | None, category: str | None, status: str | None) -> None:
    if status == "planned" and (not concept or not concept.strip() or not category or not category.strip()):
        raise HTTPException(status_code=422, detail="Idea quality gate requires concept and category before planned")


class IdeaCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    concept: str | None = None
    category: str | None = Field(default=None, max_length=100)
    hook: str | None = None
    content_warning: str | None = Field(default=None, max_length=255)


class IdeaUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    concept: str | None = None
    category: str | None = Field(default=None, max_length=100)
    hook: str | None = None
    content_warning: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=40)


@router.get("")
def list_ideas(_: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Idea).order_by(Idea.created_at.desc()).all()


@router.post("", status_code=201)
def create_idea(payload: IdeaCreate, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    values = payload.model_dump()
    item = Idea(**values)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{idea_id}")
def update_idea(idea_id: str, payload: IdeaUpdate, _: dict = Depends(require_roles("owner", "editor")), db: Session = Depends(get_db)):
    item = db.get(Idea, idea_id)
    if not item:
        raise HTTPException(status_code=404, detail="Idea not found")
    values = payload.model_dump(exclude_unset=True)
    next_status = values.get("status", item.status)
    validate_idea_gate(values.get("concept", item.concept), values.get("category", item.category), next_status)
    for key, value in values.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item
