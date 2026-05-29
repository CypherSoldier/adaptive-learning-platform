from uuid import UUID
from pydantic import BaseModel, EmailStr


class RegisterUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class GoogleToken(BaseModel):
    token: str


class TokenData(BaseModel):
    user_id: str | None = None
