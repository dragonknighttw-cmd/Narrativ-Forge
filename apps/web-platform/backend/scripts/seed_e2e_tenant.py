"""Seed a second, isolated tenant for the disposable authenticated Playwright E2E run."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.models import Organization, OrganizationMembership, User
from app.services.passwords import hash_password


email = os.environ.get("E2E_SECOND_EMAIL", "e2e-second-tenant@example.test").strip().lower()
password = os.environ.get("E2E_SECOND_PASSWORD", "E2e-Second-Password-ChangeMe1!")
if not email or not password:
    raise SystemExit("E2E_SECOND_EMAIL and E2E_SECOND_PASSWORD must be non-empty")

db = SessionLocal()
try:
    if db.query(User).filter(User.email == email).first():
        raise SystemExit("E2E second-tenant user already exists; refusing to reuse it")
    organization = Organization(
        name="E2E Isolated Workspace",
        slug="e2e-isolated-workspace",
        plan="trial",
    )
    db.add(organization)
    db.flush()
    user = User(
        email=email,
        role="owner",
        password_hash=hash_password(password),
        is_active=True,
    )
    db.add(user)
    db.flush()
    db.add(
        OrganizationMembership(
            organization_id=organization.id,
            user_id=user.id,
            role="owner",
        )
    )
    db.commit()
    print("Seeded isolated E2E tenant.")
finally:
    db.close()
