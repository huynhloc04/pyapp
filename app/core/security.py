from passlib.context import CryptContext
import os
from app.core.config import settings
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
ALGORITHM = settings.ALGORITHM
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_REFRESH_SECRET_KEY = settings.JWT_REFRESH_SECRET_KEY

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(
    subject: Union[str, Any], provider: str = None, expires_delta: int = None
) -> str:
    if expires_delta:
        expires = datetime.now() + expires_delta
    else:
        expires = datetime.now() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

    to_encode = {"exp": expires, "sub": str(subject)}
    if provider:
        to_encode = {"provider": provider, **to_encode}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any], provider: str = None, expires_delta: int = None
) -> str:
    if expires_delta:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(
            minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES)
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    if provider:
        to_encode = {"provider": provider, **to_encode}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt
