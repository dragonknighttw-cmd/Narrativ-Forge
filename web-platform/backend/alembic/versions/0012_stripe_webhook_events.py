"""idempotent Stripe webhook event storage"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0012_stripe_webhook_events"
down_revision = "0011_webhook_secret"
branch_labels = None
depends_on = None

def upgrade() -> None:
    if inspect(op.get_bind()).has_table("stripe_webhook_events"):
        return
    op.create_table(
        "stripe_webhook_events",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("event_type", sa.String(120), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
    )

def downgrade() -> None:
    op.drop_table("stripe_webhook_events")
