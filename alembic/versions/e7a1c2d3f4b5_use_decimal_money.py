"""Use decimal types for monetary values.

Revision ID: e7a1c2d3f4b5
Revises: d49d284af350
Create Date: 2026-10-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7a1c2d3f4b5"
down_revision: Union[str, Sequence[str], None] = "d49d284af350"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "products",
        "product_price",
        existing_type=sa.Float(),
        type_=sa.Numeric(12, 2),
        existing_nullable=False,
        postgresql_using="product_price::numeric(12,2)",
    )
    op.alter_column(
        "orders",
        "total",
        existing_type=sa.Float(),
        type_=sa.Numeric(12, 2),
        existing_nullable=False,
        postgresql_using="total::numeric(12,2)",
    )
    op.alter_column(
        "order_items",
        "unit_price",
        existing_type=sa.Integer(),
        type_=sa.Numeric(12, 2),
        existing_nullable=False,
        postgresql_using="unit_price::numeric(12,2)",
    )


def downgrade() -> None:
    op.alter_column(
        "order_items",
        "unit_price",
        existing_type=sa.Numeric(12, 2),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="unit_price::integer",
    )
    op.alter_column(
        "orders",
        "total",
        existing_type=sa.Numeric(12, 2),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using="total::double precision",
    )
    op.alter_column(
        "products",
        "product_price",
        existing_type=sa.Numeric(12, 2),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using="product_price::double precision",
    )
