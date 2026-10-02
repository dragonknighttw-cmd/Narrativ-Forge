from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from ..dependencies import get_current_user
from ...core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(payload: LoginRequest, response: Response):
    if payload.email != settings.dev_auth_email or payload.password != settings.dev_auth_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    response.set_cookie(
        key=settings.session_cookie_name,
        value="dev-session",
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        max_age=60 * 60 * 8,
        path="/",
    )
    return {"authenticated": True, "user": {"email": settings.dev_auth_email, "role": "owner"}}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=settings.session_cookie_name, path="/")
    return {"authenticated": False}

@router.get("/me")
def me(user=Depends(get_current_user)):
    return user
