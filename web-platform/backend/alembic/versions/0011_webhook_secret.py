"""store webhook signing secret securely for delivery"""
from alembic import op
import sqlalchemy as sa
revision = "0011_webhook_secret"
down_revision = "0010_tenant_content_scope"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("webhook_endpoints", sa.Column("secret_encrypted", sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column("webhook_endpoints", "secret_encrypted")
