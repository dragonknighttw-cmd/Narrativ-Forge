"""Allow scene numbers to repeat across script versions.

Revision ID: 0003_scene_script_scope
Revises: 0002_asset_storage_metadata
"""

from alembic import op

revision = "0003_scene_script_scope"
down_revision = "0002_asset_storage_metadata"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("scenes") as batch:
        batch.drop_constraint("uq_scene_number_per_episode", type_="unique")
        batch.create_unique_constraint("uq_scene_number_per_script", ["script_id", "scene_number"])


def downgrade():
    with op.batch_alter_table("scenes") as batch:
        batch.drop_constraint("uq_scene_number_per_script", type_="unique")
        batch.create_unique_constraint("uq_scene_number_per_episode", ["episode_id", "scene_number"])
