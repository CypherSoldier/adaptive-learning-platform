from typing import Annotated
from fastapi import APIRouter, Depends, Request
from starlette import status
from ...schemas import auth
from ...services import auth_service
from fastapi.security import OAuth2PasswordRequestForm
from ...database.session import DbSession

# from ..rate_limiter import limiter
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/", status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/hour")
async def register_user(
    request: Request, db: DbSession, register_user_request: auth.RegisterUserRequest
):
    auth_service.register_user(db, register_user_request)
    return "Account Created"


@router.post("/token", response_model=auth.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession
):
    return auth_service.login_for_access_token(form_data, db)


@router.post("/google", response_model=auth.Token)
async def login_with_google(token: auth.GoogleToken, db: DbSession):
    return auth_service.login_with_google(token, db)
