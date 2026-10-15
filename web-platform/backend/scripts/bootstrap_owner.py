#!/usr/bin/env python3
"""Create the first Narrativ Forge owner using the application's password hasher.

Run from web-platform/backend with DATABASE_URL set in your local environment:
    python -m scripts.bootstrap_owner
Optionally choose an organization:
    python scripts/bootstrap_owner.py --organization-slug legacy-workspace

The password is entered with terminal echo disabled and is never printed.
This script refuses to run if any user already exists.
"""
from __future__ import annotations

import argparse
import getpass
import re
import sys

from sqlalchemy import select, text

from app.db import SessionLocal
from app.models import Organization, OrganizationMembership, User
from app.services.passwords import hash_password


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the initial Narrativ Forge owner")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--organization-id")
    group.add_argument("--organization-slug")
    args = parser.parse_args()

    email = input("Owner email: ").strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        print("Invalid email address.", file=sys.stderr)
        return 2

    password = getpass.getpass("New owner password (minimum 12 characters): ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.", file=sys.stderr)
        return 2
    if len(password) < 12:
        print("Password must be at least 12 characters.", file=sys.stderr)
        return 2

    db = SessionLocal()
    try:
        with db.begin():
            # Serialize bootstrap attempts on PostgreSQL, so two terminals cannot
            # both observe an empty users table and create separate initial owners.
            if db.get_bind().dialect.name == "postgresql":
                db.execute(text("SELECT pg_advisory_xact_lock(739281004)"))

            if db.execute(select(User.id).limit(1)).first() is not None:
                print("Bootstrap refused: at least one user already exists. Use the normal owner invitation flow.")
                return 3

            query = select(Organization)
            if args.organization_id:
                query = query.where(Organization.id == args.organization_id)
            elif args.organization_slug:
                query = query.where(Organization.slug == args.organization_slug)
            organizations = list(db.scalars(query.order_by(Organization.created_at)).all())
            if not organizations:
                print("No matching organization found; no account was created.", file=sys.stderr)
                return 4
            if len(organizations) != 1:
                print("Multiple organizations found. Re-run with --organization-id or --organization-slug.", file=sys.stderr)
                return 4

            if db.execute(select(User.id).where(User.email == email).limit(1)).first():
                print("That email already exists; no account was created.", file=sys.stderr)
                return 5

            owner = User(
                email=email,
                role="owner",
                password_hash=hash_password(password),
                is_active=True,
            )
            db.add(owner)
            db.flush()
            db.add(
                OrganizationMembership(
                    organization_id=organizations[0].id,
                    user_id=owner.id,
                    role="owner",
                )
            )
        print("Initial owner created successfully. Keep the password private and test login in the deployed app.")
        return 0
    except Exception as exc:
        print(f"Owner bootstrap failed; transaction rolled back ({type(exc).__name__}).", file=sys.stderr)
        return 1
    finally:
        password = ""
        confirm = ""
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
