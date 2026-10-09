import pytest

pytestmark = pytest.mark.unit

from datetime import datetime, timedelta, timezone
import hashlib
import secrets

import pytest

from app.api.routes import auth
from app.models import MagicLinkToken, Organization, OrganizationMembership, User
from app.db import get_db
from app.main import app
from client_utils import create_test_client


def test_magic_link_unknown_user_does_not_enumerate(db_session):
    payload = auth.MagicLinkRequest(email="unknown@example.com")
    result = auth.request_magic_link(payload, db_session)
    assert result == {"accepted": True}


def test_magic_link_consumes_once(monkeypatch, db_session):
    raw = secrets.token_urlsafe(24)
    organization = Organization(name="Magic Link Workspace", slug="magic-link-workspace", plan="trial")
    db_session.add(organization)
    db_session.flush()
    user = User(email="magic@example.com", password_hash="x", role="editor", is_active=True)
    db_session.add(user)
    db_session.flush()
    db_session.add(OrganizationMembership(organization_id=organization.id, user_id=user.id, role="editor"))
    db_session.add(MagicLinkToken(
        email=user.email,
        token_hash=hashlib.sha256(raw.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
    ))
    db_session.commit()

    response = type("Response", (), {"set_cookie": lambda *args, **kwargs: None})()
    result = auth.consume_magic_link(raw, response, db_session)
    assert result["authenticated"] is True

    with pytest.raises(Exception):
        auth.consume_magic_link(raw, response, db_session)


def test_magic_link_delivery_failure_returns_503(monkeypatch, db_session):
    user = User(email="mailfail@example.com", password_hash="x", role="viewer", is_active=True)
    db_session.add(user)
    db_session.commit()
    monkeypatch.setattr(auth, "send_email", lambda **kwargs: (_ for _ in ()).throw(RuntimeError("smtp down")))

    with pytest.raises(Exception) as exc:
        auth.request_magic_link(auth.MagicLinkRequest(email=user.email), db_session)
    assert getattr(exc.value, "status_code", None) == 503
    assert db_session.query(MagicLinkToken).count() == 0


def test_magic_link_missing_token_returns_401(db_session):
    response = type("Response", (), {"set_cookie": lambda *args, **kwargs: None})()
    with pytest.raises(Exception) as exc:
        auth.consume_magic_link("missing-token", response, db_session)
    assert getattr(exc.value, "status_code", None) == 401
