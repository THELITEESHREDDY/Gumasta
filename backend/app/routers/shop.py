from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user, get_owned_shop
from app.models.user import User
from app.models.shop import Shop

from app.schemas.shop import (
    ShopCreate,
    ShopUpdate,
    ShopResponse
)

from app.services.shop_service import (
    create_shop,
    get_shops,
    update_shop,
    ShopNotFoundError,
    InvalidShopUpdateError
)


router = APIRouter(
    prefix="/shops",
    tags=["Shops"]
)


@router.post(
    "",
    response_model=ShopResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
    data: ShopCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await create_shop(
        db=db,
        owner_id=current_user.id,
        data=data
    )


@router.get("", response_model=list[ShopResponse])
async def list_shops(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_shops(
        db=db,
        owner_id=current_user.id
    )


@router.get("/{shop_id}", response_model=ShopResponse)
async def retrieve(
    shop: Shop = Depends(get_owned_shop)
):
    return shop


@router.patch("/{shop_id}", response_model=ShopResponse)
async def update(
    shop_id: UUID,
    data: ShopUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await update_shop(
            db=db,
            shop_id=shop_id,
            owner_id=current_user.id,
            data=data
        )

    except ShopNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Shop not found"
        )

    except InvalidShopUpdateError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )