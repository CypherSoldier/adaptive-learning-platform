from fastapi import APIRouter, status, Depends
from uuid import UUID
from sqlalchemy.orm import Session
from src.database.session import get_db
from ...database.session import DbSession
from ...services.auth_service import CurrentUser
from src.services.question_service import get_user_skill_profile
from src.services.user_service import get_user_by_id
from ...schemas.user import UserResponse
from src.services.question_service import get_user_skill_profiles
from src.services.auth_service import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user(current_user: CurrentUser, db: DbSession):
    return get_user_by_id(db, current_user.user_id)


"""
@router.put("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    password_change: models.PasswordChange,
    db: DbSession,
    current_user: CurrentUser
):
    service.change_password(db, current_user.get_uuid(), password_change)
"""


@router.get("/profile")
def get_skill_profile(user_id: int, track_id: int, db: DbSession):
    return get_user_skill_profile(user_id=user_id, track_id=track_id, db=db)


@router.get("/skill-profiles")
def get_my_skill_profiles(current_user=Depends(get_current_user), db=Depends(get_db)):
    return get_user_skill_profiles(db, current_user.user_id)
