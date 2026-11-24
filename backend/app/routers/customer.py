from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_owned_shop
from app.models.shop import Shop

from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse
)

from app.services.customer_service import (
    create_customer,
    get_customers,
    get_customer,
    update_customer,
    CustomerNotFoundError,
    DuplicateMobileError,
    InvalidCustomerUpdateError
)


router = APIRouter(
    prefix="/shops/{shop_id}/customers",
    tags=["Customers"]
)


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED
)
async def create(
    data: CustomerCreate,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await create_customer(
            db=db,
            shop_id=shop.id,
            data=data
        )

    except DuplicateMobileError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )


@router.get(
    "",
    response_model=list[CustomerResponse]
)
async def list_customers(
    search: str | None = None,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    return await get_customers(
        db=db,
        shop_id=shop.id,
        search=search
    )


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse
)
async def retrieve(
    customer_id: UUID,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await get_customer(
            db=db,
            shop_id=shop.id,
            customer_id=customer_id
        )

    except CustomerNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )


@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse
)
async def update(
    customer_id: UUID,
    data: CustomerUpdate,
    shop: Shop = Depends(get_owned_shop),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await update_customer(
            db=db,
            shop_id=shop.id,
            customer_id=customer_id,
            data=data
        )

    except CustomerNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    except DuplicateMobileError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        )

    except InvalidCustomerUpdateError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        )