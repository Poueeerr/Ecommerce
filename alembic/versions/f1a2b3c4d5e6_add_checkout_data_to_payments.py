"""Add checkout data to payments.

Revision ID: f1a2b3c4d5e6
Revises: e7a1c2d3f4b5
Create Date: 2026-10-13
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f1a2b3c4d5e6"
down_revision: str | Sequence[str] | None = "e7a1c2d3f4b5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("provider", sa.String(length=50), nullable=True))
    op.add_column(
        "payments",
        sa.Column("provider_preference_id", sa.String(length=255), nullable=True),
    )
    op.add_column("payments", sa.Column("checkout_url", sa.String(length=2048), nullable=True))
    op.create_unique_constraint(
        "uq_payments_provider_preference_id",
        "payments",
        ["provider_preference_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_payments_provider_preference_id", "payments", type_="unique")
    op.drop_column("payments", "checkout_url")
    op.drop_column("payments", "provider_preference_id")
    op.drop_column("payments", "provider")
