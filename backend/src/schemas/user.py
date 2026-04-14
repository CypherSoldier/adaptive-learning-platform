from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    full_name: str
    password_hash: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str
