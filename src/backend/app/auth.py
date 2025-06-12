from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

import os  # Import os
from app.db.session import get_db
from app.db.models import User  # User model for fetching user

# Configuration for JWT
# Load SECRET_KEY from environment variable, with a fallback for safety (though .env should be used)
SECRET_KEY = os.getenv(
    "SECRET_KEY", "a_very_default_and_insecure_secret_key_please_change"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)  # tokenUrl is the path to the login endpoint

# New scheme for optional authentication
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

from app import schemas  # Import TokenDataSchema directly

# Removed local TokenData class definition


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get(
            "sub"
        )  # "sub" is standard claim for subject (user identifier)
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenDataSchema(
            email=email
        )  # Use imported schema directly
    except JWTError:
        raise credentials_exception

    user = await User.get_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user


async def get_optional_current_user(
    token: Optional[str] = Depends(optional_oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if token is None:
        return None
    try:
        # Re-use get_current_user logic, but catch the exception
        user = await get_current_user(token, db)
        # You could also add the active check here if needed
        return user
    except HTTPException:
        # This will happen if the token is invalid or expired.
        # For an optional user, we just return None instead of failing.
        return None
