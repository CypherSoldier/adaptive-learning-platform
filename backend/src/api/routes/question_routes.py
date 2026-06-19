from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.services.question_service import list_questions, get_user_skill_profile
from src.ai_pipeline.ai_generate_mcq import generate_mcq
from src.ai_pipeline import ai_question_service
from src.services.auth_service import get_current_user, CurrentUser

router = APIRouter()


# Unauthenticated — seeded first session, no skill filtering
@router.get("/questions/{track_id}")
def get_questions(
    track_id: int,
    source: str | None = None,
    db: Session = Depends(get_db),
):
    return list_questions(db, track_id, source=source)


# Authenticated — filters questions by the user's current skill score
@router.get("/questions/{track_id}")
def get_adaptive_questions(
    track_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = int(current_user.user_id)
    profile = get_user_skill_profile(user_id, track_id, db)
    # skill_score is now actually passed — this was the missing link
    return list_questions(db, track_id, skill_score=profile.skill_score)


@router.get("/ai_questions/{track_id}")
def get_ai_generated_questions(
    track_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.user_id
    '''
    if ai_question_service.is_first_time_user(db, user_id, track_id):
        raise HTTPException(status_code=404, detail="complete_seeded_session")
    '''
    profile = get_user_skill_profile(user_id, track_id, db)

    questions = ai_question_service.generate_and_store_questions(
        db=db,
        user_id=user_id,
        track_id=track_id,
        skill_score=profile.skill_score,
        confidence_score=profile.confidence_score,
    )
    return questions