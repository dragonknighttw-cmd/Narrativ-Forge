from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ...db import get_db
from ...models import Idea
from ..dependencies import get_current_user

router = APIRouter(prefix="/ideas", tags=["ideas"])

class IdeaCreate(BaseModel):
    title: str
    concept: str | None = None
    category: str | None = None
    hook: str | None = None

@router.get("")
def list_ideas(_: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Idea).order_by(Idea.created_at.desc()).all()

@router.post("")
def create_idea(payload: IdeaCreate, _: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    item = Idea(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
