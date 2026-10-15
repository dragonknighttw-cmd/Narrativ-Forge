from types import SimpleNamespace

import pytest
from fastapi import HTTPException, Response

from app.api.routes import auth
from app.api.routes.auth import SupabaseLoginRequest
from app.core.config import settings
from app.models import Organization, OrganizationMembership, User

OWNER_ID = "000afedc-2811-4a4e-9ea0-7d24218c44f2"
OWNER_EMAIL = "dragonknight.tw@gmail.com"


def configure_owner(monkeypatch):
    monkeypatch.setattr(settings, "supabase_url", "https://example.supabase.co")
    monkeypatch.setattr(settings, "supabase_anon_key", "sb_publishable_test_key")
    monkeypatch.setattr(settings, "supabase_owner_user_id", OWNER_ID)
    monkeypatch.setattr(settings, "supabase_owner_email", OWNER_EMAIL)
    monkeypatch.setattr(settings, "supabase_owner_organization_slug", "legacy-workspace")


def test_supabase_login_provisions_only_configured_owner(db_session, monkeypatch):
    configure_owner(monkeypatch)
    db_session.add(Organization(id="org-test", name="Legacy Workspace", slug="legacy-workspace"))
    db_session.commit()
    monkeypatch.setattr(auth.requests, "get", lambda *args, **kwargs: SimpleNamespace(
        status_code=200, json=lambda: {
            "id": OWNER_ID, "email": OWNER_EMAIL, "email_confirmed_at": "2026-10-01T00:00:00Z"
        }
    ))

    response = Response()
    result = auth.supabase_login(SupabaseLoginRequest(access_token="x" * 40), response, db_session)

    user = db_session.query(User).filter(User.id == OWNER_ID).one()
    membership = db_session.query(OrganizationMembership).filter(OrganizationMembership.user_id == OWNER_ID).one()
    assert result["authenticated"] is True
    assert result["user"]["role"] == "owner"
    assert result["user"]["organization_id"] == "org-test"
    assert user.password_hash == "supabase-auth-managed"
    assert membership.role == "owner"
    assert "HttpOnly" in response.headers["set-cookie"]


def test_supabase_login_rejects_other_unmapped_user(db_session, monkeypatch):
    configure_owner(monkeypatch)
    monkeypatch.setattr(auth.requests, "get", lambda *args, **kwargs: SimpleNamespace(
        status_code=200, json=lambda: {
            "id": "11111111-1111-4111-8111-111111111111",
            "email": "someone@example.com", "email_confirmed_at": "2026-10-01T00:00:00Z"
        }
    ))
    with pytest.raises(HTTPException) as exc_info:
        auth.supabase_login(SupabaseLoginRequest(access_token="x" * 40), Response(), db_session)
    assert exc_info.value.status_code == 403
    assert db_session.query(User).count() == 0


def test_supabase_login_rejects_invalid_access_token(db_session, monkeypatch):
    configure_owner(monkeypatch)
    monkeypatch.setattr(auth.requests, "get", lambda *args, **kwargs: SimpleNamespace(
        status_code=401, json=lambda: {}
    ))
    with pytest.raises(HTTPException) as exc_info:
        auth.supabase_login(SupabaseLoginRequest(access_token="x" * 40), Response(), db_session)
    assert exc_info.value.status_code == 401
