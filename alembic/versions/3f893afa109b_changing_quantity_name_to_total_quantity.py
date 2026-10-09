"""changing quantity name to total_quantity

Revision ID: 3f893afa109b
Revises: 8a1b2c3d4e5f
Create Date: 2026-10-09 05:10:37.047560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f893afa109b'
down_revision: Union[str, Sequence[str], None] = '8a1b2c3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "inventory",
        sa.Column("total_quantity", sa.Integer(), nullable=True),
    )
    op.execute(
        "UPDATE inventory SET total_quantity = quantity "
        "WHERE total_quantity IS NULL"
    )
    op.alter_column("inventory", "total_quantity", nullable=False)
    op.drop_column("inventory", "quantity")


def downgrade() -> None:
    op.add_column(
        "inventory",
        sa.Column("quantity", sa.Integer(), nullable=True),
    )
    op.execute(
        "UPDATE inventory SET quantity = total_quantity "
        "WHERE quantity IS NULL"
    )
    op.alter_column("inventory", "quantity", nullable=False)
    op.drop_column("inventory", "total_quantity")
