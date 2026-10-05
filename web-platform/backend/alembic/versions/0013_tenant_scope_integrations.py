"""tenant-scope audit, hooks, and Google Drive connections"""
from alembic import op
import sqlalchemy as sa

revision = "0013_tenant_scope_integrations"
down_revision = "0012_stripe_webhook_events"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("audit_events", sa.Column("organization_id", sa.String(36), nullable=True))
    op.create_index("ix_audit_events_organization_id", "audit_events", ["organization_id"])
    op.create_foreign_key("fk_audit_events_organization_id", "audit_events", "organizations", ["organization_id"], ["id"], ondelete="SET NULL")

    op.add_column("hook_library", sa.Column("organization_id", sa.String(36), nullable=True))
    op.create_index("ix_hook_library_organization_id", "hook_library", ["organization_id"])
    op.create_foreign_key("fk_hook_library_organization_id", "hook_library", "organizations", ["organization_id"], ["id"], ondelete="CASCADE")

    op.drop_constraint("uq_google_drive_user", "google_drive_connections", type_="unique")
    op.add_column("google_drive_connections", sa.Column("organization_id", sa.String(36), nullable=True))
    op.create_index("ix_google_drive_connections_organization_id", "google_drive_connections", ["organization_id"])
    op.create_foreign_key("fk_google_drive_connections_organization_id", "google_drive_connections", "organizations", ["organization_id"], ["id"], ondelete="CASCADE")
    op.create_unique_constraint("uq_google_drive_org_user", "google_drive_connections", ["organization_id", "user_email"])

def downgrade() -> None:
    op.drop_constraint("fk_google_drive_connections_organization_id", "google_drive_connections", type_="foreignkey")
    op.drop_index("ix_google_drive_connections_organization_id", table_name="google_drive_connections")
    op.drop_constraint("uq_google_drive_org_user", "google_drive_connections", type_="unique")
    op.drop_column("google_drive_connections", "organization_id")
    op.create_unique_constraint("uq_google_drive_user", "google_drive_connections", ["user_email"])
    op.drop_constraint("fk_hook_library_organization_id", "hook_library", type_="foreignkey")
    op.drop_index("ix_hook_library_organization_id", table_name="hook_library")
    op.drop_column("hook_library", "organization_id")
    op.drop_constraint("fk_audit_events_organization_id", "audit_events", type_="foreignkey")
    op.drop_index("ix_audit_events_organization_id", table_name="audit_events")
    op.drop_column("audit_events", "organization_id")
