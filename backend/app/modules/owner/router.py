from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dependencies.db import get_session
from backend.app.modules.owner.models import Owner
from backend.app.modules.owner.schema import (
    OwnerRegister,
    OwnerLogin,
    OwnerUpdate,
    OwnerResponse,
    TokenResponse,
)
from .service import (
    register_owner as register_owner_service,
    login_owner as login_owner_service,
    get_owner as get_owner_service,
    update_owner as update_owner_service,
)
from  backend.app.dependencies.owner_auth import get_current_owner


router = APIRouter(
    prefix="/owner",
    tags=["Owner"],
)


@router.post(
    "/register/",
    response_model=OwnerResponse,
    status_code=201,
)
async def register_owner(
    owner_data: OwnerRegister,
    db: AsyncSession = Depends(get_session),
):
    return await register_owner_service(db, owner_data)


@router.post(
    "/login/",
    response_model=TokenResponse,
)
async def login_owner(
    credentials: OwnerLogin,
    db: AsyncSession = Depends(get_session),
):
    return await login_owner_service(db, credentials)


@router.get(
    "/owner/",
    response_model=OwnerResponse,
)
async def get_owner(
    current_owner: Owner = Depends(get_current_owner),
    db: AsyncSession = Depends(get_session),
):
    return await get_owner_service(db, current_owner.id)


@router.patch(
    "/owner/",
    response_model=OwnerResponse,
)
async def update_owner(
    owner_data: OwnerUpdate,
    current_owner: Owner = Depends(get_current_owner),
    db: AsyncSession = Depends(get_session),
):
    return await update_owner_service(
        db,
        current_owner.id,
        owner_data,
    )