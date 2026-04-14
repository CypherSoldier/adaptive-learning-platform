from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.services.question_service import list_questions

router = APIRouter()

# pull questions from utils/sample_mcq.json...where does this leave services/question_service?
@router.get("/")
def get_questions(db: Session = Depends(get_db)):
    return list_questions(db)