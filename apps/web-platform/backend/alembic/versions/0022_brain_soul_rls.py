"""Enable RLS on Brain Soul application tables.

Revision ID: 0022_brain_soul_rls
Revises: 0021_revoke_client_grants
"""
from typing import Sequence, Union

from alembic import op

revision: str = "0022_brain_soul_rls"
down_revision: Union[str, Sequence[str], None] = "0021_revoke_client_grants"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    # Browser clients use the backend API only; RLS with no client policies
    # prevents accidental direct access if privileges are later misconfigured.
    op.execute("ALTER TABLE IF EXISTS public.brain_soul_context ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE IF EXISTS public.brain_soul_syntheses ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    # Do not disable row-level security during rollback.
    return
