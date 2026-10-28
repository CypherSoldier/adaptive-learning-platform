"""finish progress backfill and remove legacy global completion

Revision ID: e81f63a20d47
Revises: d7f4a9b2c613
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "e81f63a20d47"
down_revision = "d7f4a9b2c613"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)

    # This is also safe for databases whose ORM-created tables predate Alembic.
    progress = sa.Table("user_question_progress", sa.MetaData(), autoload_with=bind)
    submissions = sa.Table("submissions", sa.MetaData(), autoload_with=bind)
    questions = sa.Table("questions", sa.MetaData(), autoload_with=bind)

    correct_answers = bind.execute(
        sa.select(submissions.c.user_id, submissions.c.question_id, questions.c.source)
        .select_from(submissions.join(questions, submissions.c.question_id == questions.c.id))
        .where(submissions.c.is_correct.is_(True))
        .distinct()
    ).all()
    for user_id, question_id, source in correct_answers:
        existing = bind.execute(
            sa.select(progress.c.id, progress.c.completed_at)
            .where(progress.c.user_id == user_id, progress.c.question_id == question_id)
        ).first()
        seeded = bool(source and str(source).startswith("sample_"))
        if existing:
            bind.execute(
                progress.update().where(progress.c.id == existing.id).values(
                    completed=True,
                    completed_at=existing.completed_at or sa.func.current_timestamp(),
                    is_seeded=sa.or_(progress.c.is_seeded, seeded),
                )
            )
        else:
            bind.execute(progress.insert().values(
                user_id=user_id,
                question_id=question_id,
                completed=True,
                completed_at=sa.func.current_timestamp(),
                is_seeded=seeded,
            ))

    onboarding = sa.Table("track_onboarding", sa.MetaData(), autoload_with=bind)
    users = sa.Table("users", sa.MetaData(), autoload_with=bind)
    tracks = sa.Table("learning_tracks", sa.MetaData(), autoload_with=bind)
    missing_onboarding = sa.select(
        users.c.user_id, tracks.c.id, sa.true()
    ).where(~sa.exists(
        sa.select(1).select_from(onboarding).where(
            onboarding.c.user_id == users.c.user_id,
            onboarding.c.track_id == tracks.c.id,
        )
    ))
    bind.execute(onboarding.insert().from_select(
        ["user_id", "track_id", "completed"], missing_onboarding
    ))

    if "completed" in {column["name"] for column in inspector.get_columns("questions")}:
        with op.batch_alter_table("questions") as batch:
            batch.drop_column("completed")


def downgrade():
    # The removed global flag cannot be safely reconstructed from per-user data.
    pass
