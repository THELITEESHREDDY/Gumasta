from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dependencies.db import get_session 
from backend.app.dependencies.owner_auth import get_current_owner

from .schema import (
    ShopCreate,
    ShopUpdate,
    ShopPublicResponse,
    ShopOwnerResponse,
)

from .service import (
    get_shops,
    create_shop,
    update_shop,
    delete_shop,
)


shop_router = APIRouter(
    prefix="/api/shop",
    tags=["Shop"],
)


# Public read endpoint: returns only non-sensitive fields.

@shop_router.get("/", response_model=ShopPublicResponse)
async def read_shop(
    shop_id: str|None = Query(default=None),
    db: AsyncSession = Depends(get_session),
):
    if not shop_id:
        return await get_shops(db=db)
    
    return await get_shops(db=db, shop_id=shop_id)


@shop_router.post("/", response_model=ShopOwnerResponse)
async def add_shop(
    shop_data: ShopCreate,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await create_shop(
        db=db,
        shop_data=shop_data,
        owner_id=current_owner.id,
    )


@shop_router.patch("/", response_model=ShopOwnerResponse)
async def edit_shop(
    shop_id: str = Query(...),
    shop_data: ShopUpdate = ...,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await update_shop(
        db=db,
        shop_id=shop_id,
        shop_data=shop_data,
        owner_id=current_owner.id,
    )


@shop_router.delete("/")
async def remove_shop(
    shop_id: str = Query(...),
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await delete_shop(
        db=db,
        shop_id=shop_id,
        owner_id=current_owner.id,
    )