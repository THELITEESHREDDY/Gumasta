from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool

from app.models.user import User
from app.schemas.auth import UserRegister
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


class EmailAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


async def get_user_by_email(
    db: AsyncSession,
    email: str
) -> User | None:

    result = await db.execute(
        select(User).where(
            User.email == email.strip().lower()
        )
    )

    return result.scalar_one_or_none()


async def register_user(
    db: AsyncSession,
    data: UserRegister
) -> User:

    email = data.email.lower()

    existing_user = await get_user_by_email(db, email)

    if existing_user:
        raise EmailAlreadyExistsError()

    hashed_password = await run_in_threadpool(
        hash_password,
        data.password
    )

    user = User(
        name=data.name,
        email=email,
        mobile=data.mobile,
        password_hash=hashed_password
    )

    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()

        if await get_user_by_email(db, email):
            raise EmailAlreadyExistsError()

        raise

    await db.refresh(user)

    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
) -> str:

    user = await get_user_by_email(db, email)

    if not user:
        raise InvalidCredentialsError()

    is_valid = await run_in_threadpool(
        verify_password,
        password,
        user.password_hash
    )

    if not is_valid:
        raise InvalidCredentialsError()

    return create_access_token(str(user.id))