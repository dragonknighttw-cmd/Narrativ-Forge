from fastapi import Header, HTTPException
from ...core.config import settings

def get_current_user(authorization: str | None = Header(default=None)):
    if authorization != "Bearer dev-session":
        raise HTTPException(status_code=401, detail="Authentication required")
    return {"id": "dev-user", "email": settings.dev_auth_email, "role": "owner"}
