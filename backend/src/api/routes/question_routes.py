from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.services.question_service import list_questions
from src.models.learning_track import LearningTrack
from src.services.session_service import create_session
from src.services.auth_service import get_current_user
from src.schemas.question import LearningSessionOut

router = APIRouter()

# Public question listing remains for guest preview and compatibility.
@router.get("/questions/{track_id}")
def get_questions(track_id: int, source: str | None = None, db: Session = Depends(get_db)):
    if not db.query(LearningTrack).filter_by(id=track_id).first():
        raise HTTPException(status_code=404, detail="Track not found")
    return list_questions(db, track_id, source=source)

@router.post("/sessions/{track_id}", response_model=LearningSessionOut)
def get_learning_session(
    track_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    idempotency_key: str = Header(..., alias="Idempotency-Key", description="Unique retry key for this user and track session."),
):
    return create_session(db, current_user.user_id, track_id, idempotency_key)

# Compatibility endpoint. New clients should use /sessions/{track_id}.
@router.post("/ai_questions/{track_id}")
def get_ai_generated_questions(
    track_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    idempotency_key: str = Header(..., alias="Idempotency-Key", description="Unique retry key for this user and track session."),
):
    result = create_session(db, current_user.user_id, track_id, idempotency_key)
    if result["session_type"] == "onboarding":
        raise HTTPException(status_code=409, detail="onboarding_incomplete")
    return result["questions"]
