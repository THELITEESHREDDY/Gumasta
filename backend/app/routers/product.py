from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_owned_shop
from app.models.shop import Shop

from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    StockAdjustment
)

from app.services.product_service import (
    create_product,
    get_products,
    get_product,
    update_product,
    adjust_stock,
    deactivate_product,
    ProductNotFoundError,
    InvalidProductUpdateError,
    InsufficientStockError
)


router = APIRouter(
    prefix="/shops/{shop_id}/products",
    tags=["Products"]
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
    data: ProductCreate,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    return await create_product(
        db=db,
        shop_id=shop.id,
        data=data
    )


@router.get("", response_model=list[ProductResponse])
async def list_products(
    include_inactive: bool = False,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    return await get_products(
        db=db,
        shop_id=shop.id,
        include_inactive=include_inactive
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
async def retrieve(
    product_id: UUID,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await get_product(
            db=db,
            shop_id=shop.id,
            product_id=product_id
        )

    except ProductNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )


@router.patch(
    "/{product_id}",
    response_model=ProductResponse
)
async def update(
    product_id: UUID,
    data: ProductUpdate,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await update_product(
            db=db,
            shop_id=shop.id,
            product_id=product_id,
            data=data
        )

    except ProductNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    except InvalidProductUpdateError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )


@router.patch(
    "/{product_id}/stock",
    response_model=ProductResponse
)
async def update_stock(
    product_id: UUID,
    data: StockAdjustment,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await adjust_stock(
            db=db,
            shop_id=shop.id,
            product_id=product_id,
            data=data
        )

    except ProductNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    except InvalidProductUpdateError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )

    except InsufficientStockError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def deactivate(
    product_id: UUID,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        await deactivate_product(
            db=db,
            shop_id=shop.id,
            product_id=product_id
        )

    except ProductNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )