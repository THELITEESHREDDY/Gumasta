from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.dependencies.db import get_session
from backend.app.dependencies.owner_auth import get_current_owner

from .schema import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
)

from .service import (
    get_customers,
    create_customer,
    update_customer,
    delete_customer,
)

customer_router = APIRouter(
    prefix="/customer",
    tags=["Customer"],
)


@customer_router.get("/")
async def read_customers(
    customer_name: str | None = None,
    customer_id: str | None = None,
    customer_phone_number: str | None = Query(
        default=None,
        min_length=10,
        max_length=10,
        pattern=r"^\d{10}$",
    ),
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await get_customers(
        db=db,
        current_owner=current_owner,
        customer_name=customer_name,
        customer_id=customer_id,
        customer_phone_number=customer_phone_number,
    )


@customer_router.post("/", response_model=CustomerResponse)
async def add_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await create_customer(
        db=db,
        customer_data=customer_data,
    )


@customer_router.patch("/", response_model=CustomerResponse)
async def edit_customer(
    customer_id: str = Query(...),
    customer_data: CustomerUpdate = ...,
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await update_customer(
        db=db,
        customer_id=customer_id,
        customer_data=customer_data,
    )


@customer_router.delete("/")
async def remove_customer(
    customer_id: str = Query(...),
    db: AsyncSession = Depends(get_session),
    current_owner=Depends(get_current_owner),
):
    return await delete_customer(
        db=db,
        customer_id=customer_id,
    )