from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..dependencies import get_current_user, issue_session, require_roles
from ...core.config import settings
from ...db import get_db
from ...models import User
from ...services.passwords import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class InviteRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "viewer"


@router.post("/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
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
        samesite="lax",
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
    db: Session = Depends(get_db),
):
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
