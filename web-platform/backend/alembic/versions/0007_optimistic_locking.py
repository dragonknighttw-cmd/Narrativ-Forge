"""Add optimistic-lock row versions to episodes and scripts."""

from alembic import op
import sqlalchemy as sa

revision = "0007_optimistic_locking"
down_revision = "0006_idempotency_keys"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "episodes",
        sa.Column("row_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )
    op.add_column(
        "scripts",
        sa.Column("row_version", sa.Integer(), nullable=False, server_default=sa.text("1")),
    )


def downgrade() -> None:
    op.drop_column("scripts", "row_version")
    op.drop_column("episodes", "row_version")
