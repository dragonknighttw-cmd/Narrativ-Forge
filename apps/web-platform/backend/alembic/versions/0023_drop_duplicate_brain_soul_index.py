"""Remove redundant Brain Soul context uniqueness constraint.

Revision ID: 0023_brain_soul_dedupe
Revises: 0022_brain_soul_rls
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0023_brain_soul_dedupe"
down_revision: Union[str, Sequence[str], None] = "0022_brain_soul_rls"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    # The unique ix_brain_soul_context_key index already enforces uniqueness.
    # Drop the duplicate unique-constraint index without changing data integrity.
    op.execute(
        "ALTER TABLE IF EXISTS public.brain_soul_context "
        "DROP CONSTRAINT IF EXISTS uq_brain_soul_context_key"
    )


def downgrade() -> None:
    # Do not recreate the duplicate index on downgrade.
    return
