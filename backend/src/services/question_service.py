from sqlalchemy.orm import Session
from src.models.question import Question
from ..models.user_skill_profile import UserSkillProfile
from ..models.topic import Topic
from src.models.learning_track import LearningTrack
from fastapi import HTTPException, Depends
from src.database.session import get_db
from src.services.auth_service import get_current_user  # ← Google user support

def list_questions(db: Session):
    return db.query(Question).all()

'''
def get_skill_profile(user_profile: UserSkillProfile = Depends()):
    return user_profile
'''
def get_user_skill_profile(user_id: int, track_id: int, db: Session):
    profile = db.query(UserSkillProfile).filter(
        UserSkillProfile.user_id == user_id,
        UserSkillProfile.track_id == track_id
    ).first()

    if not profile:
        profile = UserSkillProfile(
            user_id=user_id,
            track_id=track_id,
            skill_score=0.3,
            confidence_score=0.3,
            attempts=0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile
    

# NEW: Return ALL tracks for the current user (used by skill-profile page)
def get_user_skill_profiles(db: Session, user_id: int):
    profiles = (
        db.query(
            UserSkillProfile,
            LearningTrack.name.label("track_name"),
            LearningTrack.track_type.label("track_type")
        )
        .join(LearningTrack, LearningTrack.id == UserSkillProfile.track_id)
        .filter(UserSkillProfile.user_id == user_id)
        .all()
    )

    return [
        {
            "id": p.UserSkillProfile.id,
            "user_id": p.UserSkillProfile.user_id,
            "track_id": p.UserSkillProfile.track_id,
            "track_name": p.track_name,
            "track_type": p.track_type,
            "skill_score": p.UserSkillProfile.skill_score,
            "confidence_score": p.UserSkillProfile.confidence_score,
            "attempts": p.UserSkillProfile.attempts,
        }
        for p in profiles
    ]


def get_curated_questions_for_topic(topic_id: int, topic: Topic):
    # if topic_id matches the topic chosen
    # then fetch the questions that have matching topic_ids
    # return questions
    # profile = get_user_skill_profile(user_id, track_id, db)   # now per-track
    # curated = await get_curated_questions_for_topic(...)   # your future logic
    # return curated[0] if curated else fallback
    # return {"message": "next question logic ready – using per-track profile"}
    pass


async def get_next_question(user_id: int, track_id: int):
    profile = await get_user_skill_profile()
    curated = await get_curated_questions_for_topic(profile.topic_id, profile.skill_score)
    if curated:
        return curated[0]
    # Later → fall back to AI