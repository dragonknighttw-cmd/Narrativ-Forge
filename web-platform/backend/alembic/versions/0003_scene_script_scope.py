"""Allow scene numbers to repeat across script versions.

Revision ID: 0003_scene_script_scope
Revises: 0002_asset_storage_metadata
"""

from alembic import op
from sqlalchemy import inspect

revision = "0003_scene_script_scope"
down_revision = "0002_asset_storage_metadata"
branch_labels = None
depends_on = None


def _scene_unique_constraints() -> set[str]:
    return {
        constraint["name"]
        for constraint in inspect(op.get_bind()).get_unique_constraints("scenes")
    }


def upgrade():
    constraints = _scene_unique_constraints()
    legacy = "uq_scene_number_per_episode"
    current = "uq_scene_number_per_script"

    if legacy in constraints and current not in constraints:
        with op.batch_alter_table("scenes") as batch:
            batch.drop_constraint(legacy, type_="unique")
            batch.create_unique_constraint(current, ["script_id", "scene_number"])
    elif current not in constraints or legacy in constraints:
        raise RuntimeError("Expected exactly one known scene-number unique constraint")


def downgrade():
    constraints = _scene_unique_constraints()
    legacy = "uq_scene_number_per_episode"
    current = "uq_scene_number_per_script"

    if current in constraints and legacy not in constraints:
        with op.batch_alter_table("scenes") as batch:
            batch.drop_constraint(current, type_="unique")
            batch.create_unique_constraint(legacy, ["episode_id", "scene_number"])
    elif legacy not in constraints or current in constraints:
        raise RuntimeError("Expected exactly one known scene-number unique constraint")
