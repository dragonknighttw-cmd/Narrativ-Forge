"""Add optimistic-lock row versions to episodes and scripts."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0007_optimistic_locking"
down_revision = "0006_idempotency_keys"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for table in ("episodes", "scripts"):
        columns = {column["name"] for column in inspect(bind).get_columns(table)}
        if "row_version" not in columns:
            op.add_column(
                table,
                sa.Column(
                    "row_version",
                    sa.Integer(),
                    nullable=False,
                    server_default=sa.text("1"),
                ),
            )


def downgrade() -> None:
    bind = op.get_bind()
    for table in ("scripts", "episodes"):
        columns = {column["name"] for column in inspect(bind).get_columns(table)}
        if "row_version" in columns:
            op.drop_column(table, "row_version")
