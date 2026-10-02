from fastapi import Cookie, Depends, Header, HTTPException
from ...core.config import settings

def get_current_user(
    session_cookie: str | None = Cookie(default=None, alias=settings.session_cookie_name),
    authorization: str | None = Header(default=None),
):
    valid_session = session_cookie == "dev-session"
    valid_bearer = authorization == "Bearer dev-session"
    if not (valid_session or valid_bearer):
        raise HTTPException(status_code=401, detail="Authentication required")
    return {"id": "dev-user", "email": settings.dev_auth_email, "role": "owner"}

def require_roles(*roles: str):
    def dependency(user=Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return dependency
