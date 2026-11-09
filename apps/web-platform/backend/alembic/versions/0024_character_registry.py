"""Persist organization-scoped Character Studio registry.

Revision ID: 0024_character_registry
Revises: 0023_brain_soul_dedupe
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0024_character_registry"
down_revision: Union[str, Sequence[str], None] = "0023_brain_soul_dedupe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "character_registry",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("actor_id", sa.String(length=120), nullable=False),
        sa.Column("actor_name", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=100), server_default="Virtual Actor", nullable=False),
        sa.Column("source_studio", sa.String(length=120), server_default="AuraCraft Studio", nullable=False),
        sa.Column("voice_binding_json", sa.Text(), server_default="{}", nullable=False),
        sa.Column("vrm_model_path", sa.String(length=500), nullable=True),
        sa.Column("expression_map_json", sa.Text(), nullable=True),
        sa.Column("character_meta_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "actor_id", name="uq_character_registry_org_actor"),
    )
    op.create_index("ix_character_registry_organization_id", "character_registry", ["organization_id"], unique=False)
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TABLE public.character_registry ENABLE ROW LEVEL SECURITY")
        op.execute("""
            DO $nf$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon')
                   AND EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    EXECUTE 'REVOKE ALL PRIVILEGES ON TABLE public.character_registry FROM anon, authenticated';
                END IF;
            END $nf$;
        """)


def downgrade() -> None:
    op.drop_index("ix_character_registry_organization_id", table_name="character_registry")
    op.drop_table("character_registry")
