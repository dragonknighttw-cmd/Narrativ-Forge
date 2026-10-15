"""security and performance hardening for Supabase/PostgreSQL deployments"""
from alembic import op
import sqlalchemy as sa

revision = "0014_security_perf_hardening"
down_revision = "0013_tenant_scope_integrations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(sa.text("""
            DO $nf$
            BEGIN
              IF to_regprocedure('public.rls_auto_enable()') IS NOT NULL THEN
                EXECUTE 'REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM PUBLIC';
                EXECUTE 'REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM anon';
                EXECUTE 'REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM authenticated';
              END IF;
            END $nf$;
        """))
        bind.execute(sa.text("DROP INDEX IF EXISTS public.ix_organizations_slug"))
        bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_invitations_organization_id ON public.invitations (organization_id)"))
        bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_processing_jobs_input_asset_id ON public.processing_jobs (input_asset_id)"))
        bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_processing_jobs_output_asset_id ON public.processing_jobs (output_asset_id)"))
        bind.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_upload_sessions_scene_id ON public.upload_sessions (scene_id)"))


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(sa.text("DROP INDEX IF EXISTS public.ix_invitations_organization_id"))
        bind.execute(sa.text("DROP INDEX IF EXISTS public.ix_processing_jobs_input_asset_id"))
        bind.execute(sa.text("DROP INDEX IF EXISTS public.ix_processing_jobs_output_asset_id"))
        bind.execute(sa.text("DROP INDEX IF EXISTS public.ix_upload_sessions_scene_id"))
