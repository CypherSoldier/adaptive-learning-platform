"""persist idempotency records for AI question batches

Revision ID: b4c9d21f7e31
Revises: a73e91c04b2f
Create Date: 2026-10-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b4c9d21f7e31"
down_revision: Union[str, Sequence[str], None] = "a73e91c04b2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_generation_requests",
        sa.Column("request_id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("track_id", sa.Integer(), sa.ForeignKey("learning_tracks.id"), nullable=False),
        sa.Column("question_ids", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ai_generation_requests")
