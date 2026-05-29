import json
import logging
from sqlalchemy.orm import Session
from ..models.question import Question
from ..models.user_skill_profile import UserSkillProfile
from src.ai_pipeline.ai_generate_mcq import generate_mcq

logger = logging.getLogger(__name__)

FIRST_TIME_SKILL_THRESHOLD = 0.0
BATCH_SIZE = 15

def is_first_time_user(db: Session, user_id: int, track_id: int) -> bool:
    profile = (
    db.query(UserSkillProfile)
    .filter(
        UserSkillProfile.user_id == user_id,
        UserSkillProfile.track_id == track_id,
    )
    .first()
    )

    return profile is None or profile.skill_score == FIRST_TIME_SKILL_THRESHOLD


def generate_and_store_questions(
    db: Session,
    user_id: int,
    track_id: int,
    skill_score: float,
    confidence_score: float,
) -> list[Question]:
    
    if track_id == 1:
        topic = "Python"
    elif track_id == 2:
        topic = "C++"
    elif track_id == 3:
        topic = "JavaScript"
    
    difficulty = max(1.0, min(5.0, round(skill_score / 2, 1)))

    logger.info(f"Generating questions for user {user_id} on topic '{topic}' with skill score {skill_score} and confidence score {confidence_score}. Difficulty level: {difficulty}")

    raw_questions = generate_mcq(topic, difficulty, BATCH_SIZE)

    ai_questions = []

    for q in raw_questions:
        record = Question( 
            track_id=track_id,
            question=q["question"],
            options=q["options"],
            correct_answer=q["correct_answer"],
            explanation=q["explanation"],
            difficulty=q["difficulty"],
            source="ai_generated",
        )
        db.add(record)
        ai_questions.append(record)
    
    db.commit()
    for q in ai_questions:
        db.refresh(q)

    return ai_questions