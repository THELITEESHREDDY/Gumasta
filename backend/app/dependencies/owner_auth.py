from datetime import datetime, timedelta, timezone
from jose import jwt
from pwdlib import PasswordHash
from ..config import settings
# app/dependencies/owner_auth.py

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from backend.app.dependencies.db import get_session
from backend.app.modules.owner.models import Owner
from backend.app.config import settings


bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_owner(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> Owner:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Check whether Authorization header exists
    if credentials is None:
        raise credentials_exception

    token = credentials.credentials

    # 2. Decode and verify JWT
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
        )

        owner_id: str | None = payload.get("sub")

        if not owner_id:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # 3. Fetch owner from database
    result = await db.execute(
        select(Owner).where(Owner.id == owner_id)
    )

    owner = result.scalar_one_or_none()

    if owner is None:
        raise credentials_exception

    # 4. Return authenticated owner
    return owner

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)