from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database.session import get_db
from src.schemas.submission import SubmissionCreate, SubmissionOut, SubmissionResponse
from src.services.auth_service import get_current_user
from src.services.submission_service import submit

router = APIRouter()


@router.post("/submissions", response_model=SubmissionResponse)
def create_submission(
    submission_data: SubmissionCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return submit(db, current_user.user_id, submission_data)
