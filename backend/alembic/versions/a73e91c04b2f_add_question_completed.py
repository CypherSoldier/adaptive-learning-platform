"""add completed to questions

Revision ID: a73e91c04b2f
Revises: 2ccf31fd3122
Create Date: 2026-10-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a73e91c04b2f"
down_revision: Union[str, Sequence[str], None] = "2ccf31fd3122"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the completion flag used by the Question model."""
    op.add_column(
        "questions",
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    """Remove the completion flag."""
    op.drop_column("questions", "completed")
