from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.user_skill_profile import UserSkillProfile


def get_or_create_skill_profile(db: Session, user_id: int, track_id: int) -> UserSkillProfile:
    profile = db.query(UserSkillProfile).filter_by(user_id=user_id, track_id=track_id).first()
    if profile is not None:
        return profile

    profile = UserSkillProfile(
        user_id=user_id,
        track_id=track_id,
        skill_score=0.3,
        confidence_score=0.3,
        attempts=0,
    )
    try:
        # The unique constraint resolves simultaneous first-session requests
        # across workers. A savepoint lets the losing request continue safely.
        with db.begin_nested():
            db.add(profile)
            db.flush()
        return profile
    except IntegrityError:
        existing = db.query(UserSkillProfile).filter_by(user_id=user_id, track_id=track_id).first()
        if existing is None:
            raise
        return existing
