import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.models import Organization, OrganizationMembership, User
from app.services.passwords import hash_password


email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", "")
if not email or not password:
    raise SystemExit("Set BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD")

import subprocess
subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
db = SessionLocal()
try:
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise SystemExit("Bootstrap user already exists; refusing to overwrite it")
    user = User(email=email, role="owner", password_hash=hash_password(password), is_active=True)
    db.add(user)
    db.flush()
    organization = Organization(name="Default Workspace", slug="default-workspace", plan="trial")
    db.add(organization)
    db.flush()
    db.add(OrganizationMembership(organization_id=organization.id, user_id=user.id, role="owner"))
    db.commit()
    print(user.email)
finally:
    db.close()
