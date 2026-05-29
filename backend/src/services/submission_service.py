from sqlalchemy.orm import Session
from src.models.submission import Submission
from src.models.question import Question
from src.models.user_skill_profile import UserSkillProfile
from src.services.adaptive_engine import update_skill_after_submission
from src.schemas.submission import SubmissionCreate, SubmissionOut, SubmissionResponse
from fastapi import HTTPException


def submit(
    db: Session, user_id: int, submission_data: SubmissionCreate
) -> SubmissionResponse:

    question = (
        db.query(Question).filter(Question.id == submission_data.question_id).first()
    )
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    is_correct = question.correct_answer == submission_data.answer

    submission = Submission(
        user_id=user_id,
        question_id=submission_data.question_id,
        answer=submission_data.answer,
        is_correct=is_correct,
        track_id=submission_data.track_id,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    skill_profile = (
        db.query(UserSkillProfile)
        .filter(
            UserSkillProfile.user_id == user_id,
            UserSkillProfile.track_id == submission_data.track_id,
        )
        .first()
    )

    if not skill_profile:
        skill_profile = UserSkillProfile(
            user_id=user_id,
            track_id=submission_data.track_id,
            skill_score=0.3,
            confidence_score=0.3,
            attempts=0,
        )
        db.add(skill_profile)
        db.commit()
        db.refresh(skill_profile)

    update_skill_after_submission(skill_profile, submission)

    db.commit()
    db.refresh(skill_profile)

    return {
        "submission": SubmissionOut.model_validate(submission),
        "updated_skill_profile": {
            "track_id": skill_profile.track_id,
            "skill_score": skill_profile.skill_score,
            "confidence_score": skill_profile.confidence_score,
            "attempts": skill_profile.attempts,
        },
    }
