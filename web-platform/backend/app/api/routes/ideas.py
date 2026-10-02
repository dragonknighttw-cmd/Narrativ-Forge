from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db import get_db
from ...models import Idea
from ..dependencies import get_current_user

router = APIRouter(prefix="/ideas", tags=["ideas"])

class IdeaCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    concept: str | None = None
    category: str | None = Field(default=None, max_length=100)
    hook: str | None = None

class IdeaUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    concept: str | None = None
    category: str | None = Field(default=None, max_length=100)
    hook: str | None = None
    status: str | None = Field(default=None, max_length=40)

@router.get("")
def list_ideas(_: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Idea).order_by(Idea.created_at.desc()).all()

@router.post("", status_code=201)
def create_idea(payload: IdeaCreate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = Idea(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.patch("/{idea_id}")
def update_idea(idea_id: str, payload: IdeaUpdate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Idea, idea_id)
    if not item:
        raise HTTPException(status_code=404, detail="Idea not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item
