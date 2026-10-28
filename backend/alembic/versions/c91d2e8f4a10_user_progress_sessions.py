"""add per-user progress, onboarding, and persisted sessions

Revision ID: c91d2e8f4a10
Revises: b4c9d21f7e31
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "c91d2e8f4a10"
down_revision = "b4c9d21f7e31"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    if "completed" in {c["name"] for c in inspector.get_columns("questions")}:
        with op.batch_alter_table("questions") as batch:
            batch.drop_column("completed")

    op.create_table(
        "user_question_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("is_seeded", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("user_id", "question_id", name="uq_user_question_progress_user_question"),
    )
    op.create_table(
        "track_onboarding",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("track_id", sa.Integer(), sa.ForeignKey("learning_tracks.id"), nullable=False),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("user_id", "track_id", name="uq_track_onboarding_user_track"),
    )
    op.create_table(
        "learning_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("idempotency_key", sa.String(255), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.user_id"), nullable=False),
        sa.Column("track_id", sa.Integer(), sa.ForeignKey("learning_tracks.id"), nullable=False),
        sa.Column("session_type", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "learning_session_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("learning_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("session_id", "question_id", name="uq_session_question"),
        sa.UniqueConstraint("session_id", "position", name="uq_session_position"),
    )

    # Users present at migration time bypass seeded onboarding for every track.
    op.execute(sa.text(
        "INSERT INTO track_onboarding (user_id, track_id, completed) "
        "SELECT users.user_id, learning_tracks.id, 1 FROM users CROSS JOIN learning_tracks"
    ))
    # Correct historical answers are the only valid completion evidence.
    op.execute(sa.text(
        "INSERT INTO user_question_progress (user_id, question_id, completed, completed_at, is_seeded) "
        "SELECT s.user_id, s.question_id, 1, CURRENT_TIMESTAMP, "
        "CASE WHEN q.source LIKE 'sample_%' THEN 1 ELSE 0 END "
        "FROM submissions s JOIN questions q ON q.id = s.question_id "
        "WHERE s.is_correct IS TRUE GROUP BY s.user_id, s.question_id, q.source"
    ))


def downgrade():
    op.drop_table("learning_session_questions")
    op.drop_table("learning_sessions")
    op.drop_table("track_onboarding")
    op.drop_table("user_question_progress")
    # Deliberately do not recreate global questions.completed.


