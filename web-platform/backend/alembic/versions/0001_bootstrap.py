"""bootstrap current Narrativ Forge schema"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

from app.db import Base
from app.models import core  # noqa: F401

revision = "0001_bootstrap"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "password_hash" not in columns:
        op.add_column("users", sa.Column("password_hash", sa.Text(), nullable=True))
    if "is_active" not in columns:
        op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=True))
    if "updated_at" not in columns:
        op.add_column("users", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))
    op.execute(sa.text("UPDATE users SET password_hash = :hash WHERE password_hash IS NULL").bindparams(hash="disabled$bootstrap-required"))
    op.execute(sa.text("UPDATE users SET is_active = 1 WHERE is_active IS NULL"))

    asset_columns = {column["name"] for column in inspector.get_columns("assets")}
    if "object_key" not in asset_columns:
        op.add_column("assets", sa.Column("object_key", sa.String(length=1024), nullable=True))
    if "checksum_sha256" not in asset_columns:
        op.add_column("assets", sa.Column("checksum_sha256", sa.String(length=64), nullable=True))

def downgrade() -> None:
    raise RuntimeError("Refusing destructive downgrade of the production baseline")
