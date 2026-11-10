"""Scope usage idempotency keys to their organization.

Revision ID: 0025_usage_event_org_idempotency
Revises: 0024_character_registry
"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "0025_usage_event_org_idempotency"
down_revision: Union[str, Sequence[str], None] = "0024_character_registry"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    unique_constraints = inspector.get_unique_constraints("usage_events")
    global_constraint = next(
        (item for item in unique_constraints if item.get("column_names") == ["idempotency_key"]),
        None,
    )
    if bind.dialect.name == "sqlite":
        if global_constraint is not None:
            with op.batch_alter_table(
                "usage_events",
                naming_convention={"uq": "uq_%(table_name)s_%(column_0_name)s"},
            ) as batch_op:
                batch_op.drop_constraint("uq_usage_events_idempotency_key", type_="unique")
                batch_op.create_unique_constraint(
                    "uq_usage_event_org_idempotency", ["organization_id", "idempotency_key"]
                )
        return
    if global_constraint is not None and global_constraint.get("name"):
        op.drop_constraint(global_constraint["name"], "usage_events", type_="unique")
    if not any(item.get("name") == "uq_usage_event_org_idempotency" for item in unique_constraints):
        op.create_unique_constraint(
            "uq_usage_event_org_idempotency", "usage_events", ["organization_id", "idempotency_key"]
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    unique_constraints = inspector.get_unique_constraints("usage_events")
    scoped = next(
        (item for item in unique_constraints if item.get("name") == "uq_usage_event_org_idempotency"),
        None,
    )
    if bind.dialect.name == "sqlite":
        if scoped is not None:
            with op.batch_alter_table(
                "usage_events",
                naming_convention={"uq": "uq_%(table_name)s_%(column_0_name)s"},
            ) as batch_op:
                batch_op.drop_constraint("uq_usage_event_org_idempotency", type_="unique")
                batch_op.create_unique_constraint("uq_usage_events_idempotency_key", ["idempotency_key"])
        return
    if scoped is not None:
        op.drop_constraint("uq_usage_event_org_idempotency", "usage_events", type_="unique")
        op.create_unique_constraint("uq_usage_events_idempotency_key", "usage_events", ["idempotency_key"])
