# auth_service.py
from datetime import timedelta, datetime, timezone
from typing import Annotated
import os
import jwt
from jwt import PyJWTError
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.models.user import User
from ..schemas import auth
from ..schemas import user as user_schema
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from ..exceptions import AuthenticationError
import logging

SECRET_KEY = "sadasd_secret_"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# JWK Set endpoint — keys in JSON Web Key format.
FIREBASE_JWKS_URL = "https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com"
FIREBASE_PROJECT_ID = "fitness-auth-312aa"

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Password helpers
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


# Email / password auth
def authenticate_user(email: str, password: str, db: Session) -> "User | bool":
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        logging.warning(f"Failed authentication attempt for email: {email}")
        return False
    return user


def create_access_token(email: str, user_id: int, expires_delta: timedelta) -> str:
    payload = {
        "sub": email,
        "id": str(user_id),
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> auth.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        return auth.TokenData(user_id=user_id)
    except PyJWTError as e:
        logging.warning(f"Token verification failed: {str(e)}")
        raise AuthenticationError()


def register_user(db: Session, register_user_request: auth.RegisterUserRequest) -> None:
    try:
        user = User(
            email=register_user_request.email,
            full_name=register_user_request.full_name,
            password_hash=get_password_hash(register_user_request.password),
        )
        db.add(user)
        db.commit()
    except Exception as e:
        logging.error(
            f"Failed to register user: {register_user_request.email}. Error: {str(e)}"
        )
        raise


def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> auth.TokenData:
    return verify_token(token)


CurrentUser = Annotated[auth.TokenData, Depends(get_current_user)]


def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session
) -> auth.Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise AuthenticationError()
    token = create_access_token(user.email, user.user_id, timedelta(minutes=60))
    return auth.Token(access_token=token, token_type="bearer")


# Google / Firebase auth
jwks_client = jwt.PyJWKClient(FIREBASE_JWKS_URL)


def verify_firebase_id_token(id_token: str) -> dict:
    try:
        print("RAW TOKEN PAYLOAD:")
        print(jwt.decode(id_token, options={"verify_signature": False}))

        signing_key = jwks_client.get_signing_key_from_jwt(id_token)

        payload = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=FIREBASE_PROJECT_ID,
            issuer=f"https://securetoken.google.com/{FIREBASE_PROJECT_ID}",
        )

        print("VERIFIED PAYLOAD:", payload)
        return payload

    except Exception as e:
        import traceback

        traceback.print_exc()
        raise AuthenticationError("Invalid Firebase ID token")


def login_with_google(token: auth.GoogleToken, db: Session) -> auth.Token:
    """
    Accepts a Firebase ID token from the client (firebaseUser.getIdToken()), verifies it, then finds or creates the user and returns a signed app JWT.

    User lookup is by email only — the current User model has no firebase_uid column.
    """
    payload = verify_firebase_id_token(token.token)

    email = payload.get("email")
    full_name = payload.get("name", "Google User")

    if not email:
        raise AuthenticationError("Firebase token does not contain email")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            full_name=full_name,
            password_hash="",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(user.email, user.user_id, timedelta(minutes=60))
    return auth.Token(
        access_token=access_token,
        token_type="bearer",
        user=user_schema.UserResponse(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            password_hash=user.password_hash,
        ),
    )
