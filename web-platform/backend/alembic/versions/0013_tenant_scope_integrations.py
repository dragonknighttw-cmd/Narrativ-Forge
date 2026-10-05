"""tenant-scope audit, hooks, and Google Drive connections"""
from alembic import op
import sqlalchemy as sa

revision = "0013_tenant_scope_integrations"
down_revision = "0012_stripe_webhook_events"
branch_labels = None
depends_on = None

def upgrade() -> None:
    with op.batch_alter_table("audit_events") as batch:
        batch.add_column(sa.Column("organization_id", sa.String(36), nullable=True))
        batch.create_index("ix_audit_events_organization_id", ["organization_id"])
        batch.create_foreign_key(
            "fk_audit_events_organization_id",
            "organizations",
            ["organization_id"],
            ["id"],
            ondelete="SET NULL",
        )

    bind = op.get_bind()
    bind.execute(sa.text(
        "UPDATE audit_events SET organization_id = (SELECT om.organization_id FROM organization_memberships om JOIN users u ON u.id = om.user_id WHERE u.email = audit_events.actor_email ORDER BY om.created_at LIMIT 1) WHERE organization_id IS NULL"
    ))

    with op.batch_alter_table("hook_library") as batch:
        batch.add_column(sa.Column("organization_id", sa.String(36), nullable=True))
        batch.create_index("ix_hook_library_organization_id", ["organization_id"])
        batch.create_foreign_key(
            "fk_hook_library_organization_id",
            "organizations",
            ["organization_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("google_drive_connections") as batch:
        batch.drop_constraint("uq_google_drive_user", type_="unique")
        batch.add_column(sa.Column("organization_id", sa.String(36), nullable=True))
        batch.create_index("ix_google_drive_connections_organization_id", ["organization_id"])
        batch.create_foreign_key(
            "fk_google_drive_connections_organization_id",
            "organizations",
            ["organization_id"],
            ["id"],
            ondelete="CASCADE",
        )
        batch.create_unique_constraint(
            "uq_google_drive_org_user",
            ["organization_id", "user_email"],
        )

    bind = op.get_bind()
    connections = bind.execute(sa.text("SELECT id, user_email FROM google_drive_connections WHERE organization_id IS NULL")).fetchall()
    for connection_id, email in connections:
        membership = bind.execute(sa.text(
            "SELECT om.organization_id FROM organization_memberships om JOIN users u ON u.id = om.user_id WHERE u.email = :email ORDER BY om.created_at LIMIT 1"
        ), {"email": email}).first()
        if membership:
            bind.execute(sa.text(
                "UPDATE google_drive_connections SET organization_id = :organization_id WHERE id = :id"
            ), {"organization_id": membership[0], "id": connection_id})

def downgrade() -> None:
    with op.batch_alter_table("google_drive_connections") as batch:
        batch.drop_constraint("uq_google_drive_org_user", type_="unique")
        batch.drop_constraint("fk_google_drive_connections_organization_id", type_="foreignkey")
        batch.drop_index("ix_google_drive_connections_organization_id")
        batch.drop_column("organization_id")
        batch.create_unique_constraint("uq_google_drive_user", ["user_email"])

    with op.batch_alter_table("hook_library") as batch:
        batch.drop_constraint("fk_hook_library_organization_id", type_="foreignkey")
        batch.drop_index("ix_hook_library_organization_id")
        batch.drop_column("organization_id")

    with op.batch_alter_table("audit_events") as batch:
        batch.drop_constraint("fk_audit_events_organization_id", type_="foreignkey")
        batch.drop_index("ix_audit_events_organization_id")
        batch.drop_column("organization_id")
