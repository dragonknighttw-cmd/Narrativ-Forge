"""Repair the legacy scene-number uniqueness constraint.

Older databases may still have uniqueness scoped by episode. The current
schema is scoped by script, matching the Scene model and the fresh baseline.
"""

from alembic import op
from sqlalchemy import inspect


revision = "0016_repair_legacy_scene_constraint"
down_revision = "0015_revoke_public_table_grants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    constraints = {
        item.get("name")
        for item in inspector.get_unique_constraints("scenes")
    }

    if "uq_scene_number_per_episode" in constraints:
        with op.batch_alter_table("scenes") as batch:
            batch.drop_constraint("uq_scene_number_per_episode", type_="unique")

    inspector = inspect(bind)
    constraints = {
        item.get("name")
        for item in inspector.get_unique_constraints("scenes")
    }
    if "uq_scene_number_per_script" not in constraints:
        with op.batch_alter_table("scenes") as batch:
            batch.create_unique_constraint(
                "uq_scene_number_per_script",
                ["script_id", "scene_number"],
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    constraints = {
        item.get("name")
        for item in inspector.get_unique_constraints("scenes")
    }
    if "uq_scene_number_per_script" in constraints:
        with op.batch_alter_table("scenes") as batch:
            batch.drop_constraint("uq_scene_number_per_script", type="unique")
