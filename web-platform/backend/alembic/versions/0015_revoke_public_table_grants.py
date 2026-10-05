"""Revoke direct public-role table access.

The API accesses PostgreSQL through the backend service role. Public Data API
roles must not have direct CRUD access to application tables.
"""

from alembic import op


revision = "0015_revoke_public_table_grants"
down_revision = "0014_security_perf_hardening"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute(
        """
        DO $nf$
        DECLARE r record;
        BEGIN
          IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon')
             AND EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
            FOR r IN
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
          LOOP
            EXECUTE format(
              'REVOKE ALL PRIVILEGES ON TABLE %I.%I FROM anon, authenticated',
              r.table_schema,
              r.table_name
            );
            END LOOP;
          END IF;
        END $nf$;
        """
    )


def downgrade() -> None:
    # Deliberately do not restore broad public CRUD grants.
    pass
