"""tenant-scope audit, hooks, and Google Drive connections"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0013_tenant_scope_integrations"
down_revision = "0012_stripe_webhook_events"
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "organization_id" not in {column["name"] for column in inspector.get_columns("audit_events")}:
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

    if "organization_id" not in {column["name"] for column in inspector.get_columns("hook_library")}:
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

    if "organization_id" not in {column["name"] for column in inspector.get_columns("google_drive_connections")}:
        with op.batch_alter_table("google_drive_connections") as batch:
            constraints = {item.get("name") for item in inspector.get_unique_constraints("google_drive_connections")}
            if "uq_google_drive_user" in constraints:
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
    bind = op.get_bind()

    def drop_tenant_scope(table_name: str, *, unique_name: str | None = None, unique_columns: list[str] | None = None) -> None:
        inspector = sa.inspect(bind)
        columns = {column["name"] for column in inspector.get_columns(table_name)}
        if "organization_id" not in columns:
            return
        foreign_keys = {fk.get("name") for fk in inspector.get_foreign_keys(table_name)}
        indexes = {index.get("name") for index in inspector.get_indexes(table_name)}
        uniques = {constraint.get("name") for constraint in inspector.get_unique_constraints(table_name)}
        with op.batch_alter_table(table_name) as batch:
            if unique_name and unique_name in uniques:
                batch.drop_constraint(unique_name, type_="unique")
            fk_name = f"fk_{table_name}_organization_id"
            if fk_name in foreign_keys:
                batch.drop_constraint(fk_name, type_="foreignkey")
            index_name = f"ix_{table_name}_organization_id"
            if index_name in indexes:
                batch.drop_index(index_name)
            batch.drop_column("organization_id")
            if unique_columns and unique_name and unique_name not in uniques:
                batch.create_unique_constraint(unique_name, unique_columns)

    drop_tenant_scope(
        "google_drive_connections",
        unique_name="uq_google_drive_org_user",
        unique_columns=["user_email"],
    )
    drop_tenant_scope("hook_library")
    drop_tenant_scope("audit_events")
