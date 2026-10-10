"""Safely reconcile tenant scope for integrations with ambiguous memberships.

Revision ID: 0018_tenant_backfill_guard
Revises: 0017_release_maturity

Rows are assigned only when an email resolves to exactly one membership.
Ambiguous rows are left unscoped for explicit reconciliation rather than
silently attributing data to an arbitrary tenant.
"""
from alembic import op
import sqlalchemy as sa

revision = "0018_tenant_backfill_guard"
down_revision = "0017_release_maturity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # Clear prior first-membership guesses for users who belong to multiple
    # organizations. Nullable tenant scope is safer than cross-tenant attribution.
    bind.execute(sa.text("""
        UPDATE audit_events
        SET organization_id = NULL
        WHERE actor_email IN (
            SELECT u.email
            FROM users u
            JOIN organization_memberships om ON om.user_id = u.id
            GROUP BY u.email
            HAVING COUNT(DISTINCT om.organization_id) > 1
        )
    """))
    # Reconcile only emails with exactly one distinct organization membership.
    bind.execute(sa.text("""
        UPDATE audit_events
        SET organization_id = (
            SELECT MIN(om.organization_id)
            FROM organization_memberships om
            JOIN users u ON u.id = om.user_id
            WHERE u.email = audit_events.actor_email
            GROUP BY u.email
            HAVING COUNT(DISTINCT om.organization_id) = 1
        )
        WHERE actor_email IN (
            SELECT u.email
            FROM users u
            JOIN organization_memberships om ON om.user_id = u.id
            GROUP BY u.email
            HAVING COUNT(DISTINCT om.organization_id) = 1
        )
    """))

    bind.execute(sa.text("""
        UPDATE google_drive_connections
        SET organization_id = NULL
        WHERE user_email IN (
            SELECT u.email
            FROM users u
            JOIN organization_memberships om ON om.user_id = u.id
            GROUP BY u.email
            HAVING COUNT(DISTINCT om.organization_id) > 1
        )
    """))
    bind.execute(sa.text("""
        UPDATE google_drive_connections
        SET organization_id = (
            SELECT MIN(om.organization_id)
            FROM organization_memberships om
            JOIN users u ON u.id = om.user_id
            WHERE u.email = google_drive_connections.user_email
            GROUP BY u.email
            HAVING COUNT(DISTINCT om.organization_id) = 1
        )
        WHERE user_email IN (
            SELECT u.email
            FROM users u
            JOIN organization_memberships om ON om.user_id = u.id
            GROUP BY u.email
            HAVING COUNT(DISTINCT om.organization_id) = 1
        )
    """))


def downgrade() -> None:
    # Reversing would require restoring unsafe guesses. Keep corrected NULLs;
    # a downgrade must not reintroduce ambiguous cross-tenant attribution.
    pass
