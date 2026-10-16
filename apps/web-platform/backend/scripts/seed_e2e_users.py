"""Seed deterministic users/workspaces for the disposable SQLite Playwright E2E run.

This is not an application bootstrap or production provisioning command. It refuses
to run unless APP_ENV=testing and DATABASE_URL points to SQLite. Production Owner
provisioning is handled by the verified Supabase Auth login flow.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

app_env = os.environ.get("APP_ENV", "").strip().lower()
database_url = os.environ.get("DATABASE_URL", "").strip().lower()
if app_env != "testing" or not database_url.startswith("sqlite:"):
    raise SystemExit("E2E seeding is restricted to APP_ENV=testing with a SQLite DATABASE_URL")

owner_email = os.environ.get("E2E_EMAIL", "").strip().lower()
owner_password = os.environ.get("E2E_PASSWORD", "")
second_email = os.environ.get("E2E_SECOND_EMAIL", "e2e-second-tenant@example.test").strip().lower()
second_password = os.environ.get("E2E_SECOND_PASSWORD", "E2e-Second-Password-ChangeMe1!")
if not all((owner_email, owner_password, second_email, second_password)):
    raise SystemExit("E2E_EMAIL, E2E_PASSWORD, E2E_SECOND_EMAIL and E2E_SECOND_PASSWORD must be non-empty")
if owner_email == second_email:
    raise SystemExit("E2E owner and second-tenant emails must be different")

from app.db import SessionLocal
from app.models import Organization, OrganizationMembership, User
from app.services.passwords import hash_password


db = SessionLocal()
try:
    existing_user = db.query(User).filter(User.email.in_([owner_email, second_email])).first()
    if existing_user:
        raise SystemExit("E2E user already exists; refusing to reuse or overwrite it")
    existing_org = db.query(Organization).filter(
        Organization.slug.in_(["default-workspace", "e2e-isolated-workspace"])
    ).first()
    if existing_org:
        raise SystemExit("E2E workspace already exists; refusing to reuse or overwrite it")

    owner_org = Organization(name="Default Workspace", slug="default-workspace", plan="trial")
    second_org = Organization(
        name="E2E Isolated Workspace",
        slug="e2e-isolated-workspace",
        plan="trial",
    )
    db.add_all([owner_org, second_org])
    db.flush()

    owner = User(
        email=owner_email,
        role="owner",
        password_hash=hash_password(owner_password),
        is_active=True,
    )
    second = User(
        email=second_email,
        role="owner",
        password_hash=hash_password(second_password),
        is_active=True,
    )
    db.add_all([owner, second])
    db.flush()
    db.add_all([
        OrganizationMembership(
            organization_id=owner_org.id,
            user_id=owner.id,
            role="owner",
        ),
        OrganizationMembership(
            organization_id=second_org.id,
            user_id=second.id,
            role="owner",
        ),
    ])
    db.commit()
    print("Seeded isolated E2E users/workspaces.")
finally:
    db.close()
