"""Merge payments and checkout migration heads.

Revision ID: c7d8e9f0a1b2
Revises: 93caebc10ab8, f1a2b3c4d5e6
Create Date: 2026-10-13
"""

from collections.abc import Sequence

revision: str = "c7d8e9f0a1b2"
down_revision: tuple[str, str] = ("93caebc10ab8", "f1a2b3c4d5e6")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
