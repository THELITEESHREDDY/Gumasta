from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from .models import Owner
from .schema import (
    OwnerRegister,
    OwnerLogin,
    OwnerUpdate,
)
from backend.app.dependencies.owner_auth import (
    hash_password,
    verify_password,
    create_access_token,
)


async def register_owner(
    db: AsyncSession,
    owner_data: OwnerRegister,
):
    # Check whether email already exists
    result = await db.execute(
        select(Owner).where(Owner.email == str(owner_data.email))
    )
    existing_email = result.scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Check whether phone number already exists
    result = await db.execute(
        select(Owner).where(
            Owner.phone_number == owner_data.phone_number
        )
    )
    existing_phone = result.scalar_one_or_none()

    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered",
        )

    owner = Owner(
        id=str(uuid4()),
        name=owner_data.name,
        email=str(owner_data.email),
        password=hash_password(owner_data.password),
        phone_number=owner_data.phone_number,
        is_verified=False,
    )

    db.add(owner)

    try:
        await db.commit()
        await db.refresh(owner)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or phone number already registered",
        )

    return owner


async def login_owner(
    db: AsyncSession,
    credentials: OwnerLogin,
):
    result = await db.execute(
        select(Owner).where(
            Owner.email == str(credentials.email)
        )
    )

    owner = result.scalar_one_or_none()

    if not owner or not verify_password(
        credentials.password,
        owner.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": owner.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


async def get_owner(
    db: AsyncSession,
    owner_id: str,
):
    result = await db.execute(
        select(Owner).where(Owner.id == owner_id)
    )

    owner = result.scalar_one_or_none()

    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found",
        )

    return owner


async def update_owner(
    db: AsyncSession,
    owner_id: str,
    owner_data: OwnerUpdate,
):
    owner = await get_owner(db, owner_id)

    # Only fields explicitly supplied by the client
    update_data = owner_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    # Prevent explicitly supplied null values
    if any(value is None for value in update_data.values()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Profile fields cannot be null",
        )

    # Check email uniqueness if email is changing
    if "email" in update_data:
        new_email = str(update_data["email"])

        result = await db.execute(
            select(Owner).where(
                Owner.email == new_email,
                Owner.id != owner_id,
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        update_data["email"] = new_email

    # Check phone uniqueness if phone is changing
    if "phone_number" in update_data:
        result = await db.execute(
            select(Owner).where(
                Owner.phone_number == update_data["phone_number"],
                Owner.id != owner_id,
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already registered",
            )

    for field, value in update_data.items():
        setattr(owner, field, value)

    try:
        await db.commit()
        await db.refresh(owner)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or phone number already registered",
        )

    return owner