"""Revoke direct Supabase client table/sequence access.

Revision ID: 0021_revoke_client_grants
Revises: 0020_brain_soul

The application accesses its data through the backend API. The browser uses
Supabase Auth for identity only; it must not have direct PostgREST table access.
RLS remains enabled as defense in depth. This migration does not grant access to
the service_role and is intentionally non-restorative on downgrade.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0021_revoke_client_grants"
down_revision: Union[str, Sequence[str], None] = "0020_brain_soul"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # RLS with no policies already denies client row access, but explicit
    # privilege revocation removes unnecessary access grants and avoids relying
    # on policy absence as the only guard. The backend uses its server-side DB
    # credentials; browser roles anon/authenticated must use the API instead.
    # Vanilla PostgreSQL CI does not define Supabase's API roles. Skip there;
    # the migration still runs normally on Supabase where both roles exist.
    op.execute("""
        DO $body$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon')
               AND EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                EXECUTE 'REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM anon, authenticated';
                EXECUTE 'REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated';
            END IF;
        END
        $body$
    """)


def downgrade() -> None:
    # Do not restore broad client grants during rollback. Re-granting direct
    # table access requires a reviewed, table-specific access policy.
    return
