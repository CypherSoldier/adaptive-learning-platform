"""enforce one skill profile per user and track

Revision ID: d7f4a9b2c613
Revises: c91d2e8f4a10
"""
from alembic import op
import sqlalchemy as sa

revision = "d7f4a9b2c613"
down_revision = "c91d2e8f4a10"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    profiles = sa.table(
        "user_skill_profile",
        sa.column("id", sa.Integer),
        sa.column("user_id", sa.Integer),
        sa.column("track_id", sa.Integer),
        sa.column("skill_score", sa.Float),
        sa.column("confidence_score", sa.Float),
        sa.column("attempts", sa.Integer),
    )
    duplicates = bind.execute(
        sa.select(profiles.c.user_id, profiles.c.track_id)
        .group_by(profiles.c.user_id, profiles.c.track_id)
        .having(sa.func.count() > 1)
    ).all()
    for user_id, track_id in duplicates:
        rows = bind.execute(
            sa.select(profiles)
            .where(profiles.c.user_id == user_id, profiles.c.track_id == track_id)
            .order_by(sa.func.coalesce(profiles.c.attempts, 0).desc(), profiles.c.id.desc())
        ).mappings().all()
        survivor = rows[0]
        total_attempts = sum(row["attempts"] or 0 for row in rows)
        bind.execute(
            profiles.update().where(profiles.c.id == survivor["id"])
            .values(attempts=total_attempts)
        )
        bind.execute(
            profiles.delete().where(
                profiles.c.user_id == user_id,
                profiles.c.track_id == track_id,
                profiles.c.id != survivor["id"],
            )
        )
    with op.batch_alter_table("user_skill_profile") as batch:
        batch.create_unique_constraint("uq_user_skill_profile_user_track", ["user_id", "track_id"])


def downgrade():
    with op.batch_alter_table("user_skill_profile") as batch:
        batch.drop_constraint("uq_user_skill_profile_user_track", type_="unique")
