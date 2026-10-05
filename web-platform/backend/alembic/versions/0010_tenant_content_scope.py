"""tenant root backfill for existing content"""
from alembic import op
import sqlalchemy as sa

revision = "0010_tenant_content_scope"
down_revision = "0009_phase4_foundations"
branch_labels = None
depends_on = None

LEGACY_ORG_ID = "00000000-0000-0000-0000-000000000010"

def upgrade() -> None:
    bind = op.get_bind()
    for table in ("ideas", "series", "episodes"):
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("organization_id", sa.String(36), nullable=True))
            batch.create_index(f"ix_{table}_organization_id", ["organization_id"])
            batch.create_foreign_key(
                f"fk_{table}_organization_id",
                "organizations",
                ["organization_id"],
                ["id"],
            )

    bind.execute(sa.text(
        "INSERT INTO organizations (id, name, slug, plan, created_at, updated_at) "
        "VALUES (:id, :name, :slug, :plan, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
    ), {"id": LEGACY_ORG_ID, "name": "Legacy Workspace", "slug": "legacy-workspace", "plan": "trial"})

    # Membership ids are generated per user to preserve the primary-key invariant.
    rows = bind.execute(sa.text("SELECT id, role FROM users")).fetchall()
    import uuid
    for user_id, role in rows:
        bind.execute(sa.text(
            "INSERT INTO organization_memberships (id, organization_id, user_id, role, created_at) "
            "VALUES (:id, :org_id, :user_id, :role, CURRENT_TIMESTAMP)"
        ), {"id": str(uuid.uuid4()), "org_id": LEGACY_ORG_ID, "user_id": user_id, "role": role})

    bind.execute(sa.text("UPDATE ideas SET organization_id = :org_id WHERE organization_id IS NULL"), {"org_id": LEGACY_ORG_ID})
    bind.execute(sa.text("UPDATE series SET organization_id = :org_id WHERE organization_id IS NULL"), {"org_id": LEGACY_ORG_ID})
    bind.execute(sa.text("UPDATE episodes SET organization_id = :org_id WHERE organization_id IS NULL"), {"org_id": LEGACY_ORG_ID})

def downgrade() -> None:
    for table in ("episodes", "series", "ideas"):
        with op.batch_alter_table(table) as batch:
            batch.drop_constraint(f"fk_{table}_organization_id", type_="foreignkey")
            batch.drop_index(f"ix_{table}_organization_id")
            batch.drop_column("organization_id")
