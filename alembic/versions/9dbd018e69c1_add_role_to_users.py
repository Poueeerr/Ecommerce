"""add role to users

Revision ID: 9dbd018e69c1
Revises: 04947fb21204
Create Date: 2026-09-19 06:28:51.077148

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9dbd018e69c1"
down_revision: str | Sequence[str] | None = "04947fb21204"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.Enum("user", "admin", name="userrole", native_enum=False),
            nullable=False,
            server_default="user",
        ),
    )
    op.create_check_constraint("userrole", "users", "role IN ('user', 'admin')")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("userrole", "users", type_="check")
    op.drop_column("users", "role")
