from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models.submission import Submission
from src.models.question import Question
from src.models.user_question_progress import UserQuestionProgress, TrackOnboarding, LearningSession, LearningSessionQuestion
from src.services.adaptive_engine import update_skill_after_submission
from src.schemas.submission import SubmissionCreate, SubmissionOut
from src.services.skill_profile_service import get_or_create_skill_profile


def submit(db: Session, user_id: int, submission_data: SubmissionCreate):
    user_id = int(user_id)
    question = db.query(Question).filter(Question.id == submission_data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.track_id != submission_data.track_id:
        raise HTTPException(status_code=409, detail="Question does not belong to submitted track")
    progress = db.query(UserQuestionProgress).filter_by(user_id=user_id, question_id=question.id).first()
    if progress is None:
        raise HTTPException(status_code=403, detail="Question is not assigned to this user")
    if submission_data.session_id is not None:
        membership = (db.query(LearningSessionQuestion)
            .join(LearningSession, LearningSession.id == LearningSessionQuestion.session_id)
            .filter(LearningSession.id == submission_data.session_id,
                    LearningSession.user_id == user_id,
                    LearningSession.track_id == question.track_id,
                    LearningSessionQuestion.question_id == question.id).first())
        if membership is None:
            raise HTTPException(status_code=403, detail="Question is not part of this session")

    is_correct = question.correct_answer == submission_data.answer
    profile = get_or_create_skill_profile(db, user_id, question.track_id)
    submission = Submission(user_id=user_id, question_id=question.id, answer=submission_data.answer, is_correct=is_correct, track_id=question.track_id)
    db.add(submission)
    if is_correct and not progress.completed:
        progress.completed = True
        progress.completed_at = datetime.now(timezone.utc)
    update_skill_after_submission(profile, submission)
    onboarding = db.query(TrackOnboarding).filter_by(user_id=user_id, track_id=question.track_id).first()
    if onboarding is not None and not onboarding.completed:
        # Onboarding is a one-time assessment: an incorrect answer still counts
        # as an attempt, but does not mark the question solved for normal progress.
        db.flush()
        assessed = (db.query(Submission.question_id)
            .join(Question, Question.id == Submission.question_id)
            .join(UserQuestionProgress,
                  (UserQuestionProgress.question_id == Submission.question_id)
                  & (UserQuestionProgress.user_id == Submission.user_id))
            .filter(Submission.user_id == user_id,
                    Submission.track_id == question.track_id,
                    Question.track_id == question.track_id,
                    UserQuestionProgress.is_seeded.is_(True))
            .distinct().count())
        if assessed == 15:
            onboarding.completed = True
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(submission)
    db.refresh(profile)
    return {
        "submission": SubmissionOut.model_validate(submission),
        "updated_skill_profile": {"track_id": profile.track_id, "skill_score": profile.skill_score,
                                  "confidence_score": profile.confidence_score, "attempts": profile.attempts},
    }
