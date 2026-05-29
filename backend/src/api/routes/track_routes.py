from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.services.track_service import list_tracks

router = APIRouter()


# pull questions from utils/sample_mcq.json
# services/question_service not in use
@router.get("/learning_tracks")
def get_tracks(db: Session = Depends(get_db)):
    return list_tracks(db)
