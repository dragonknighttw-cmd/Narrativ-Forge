from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..dependencies import get_current_user

from ...core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(payload: LoginRequest):
    if payload.email != settings.dev_auth_email or payload.password != settings.dev_auth_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": "dev-session", "token_type": "bearer"}

@router.get("/me")
def me(user=__import__("fastapi").Depends(get_current_user)):
    return user
