from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List
from .models import Customer
from .schema import CustomerCreate, CustomerUpdate,CustomerResponse
from uuid import uuid4

async def get_customers(
    db: AsyncSession,
    current_owner,
    customer_name: str | None = None,
    customer_id: str | None = None,
    customer_phone_number: str | None = None,
)->List[CustomerResponse]:
    
    # Customer access: phone number is mandatory.
    if current_owner is None:
        if not customer_phone_number:
            raise HTTPException(
                status_code=401,
                detail="Mobile number verification required",
            )

        result = await db.execute(
            select(Customer).where(
                Customer.phone_number == customer_phone_number
            )
        )

        customer = result.scalar_one_or_none()

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found",
            )

        return [customer]

    # Owner access: can search all customers.
    query = select(Customer)

    if customer_id:
        query = query.where(Customer.id == customer_id)

    if customer_phone_number:
        query = query.where(
            Customer.phone_number == customer_phone_number
        )

    if customer_name:
        query = query.where(
            Customer.name.ilike(f"%{customer_name}%")
        )

    result = await db.execute(query)
    customers = result.scalars().all()

    if customer_id or customer_phone_number:
        if not customers:
            raise HTTPException(
                status_code=404,
                detail="Customer not found",
            )
        return customers

    return customers


async def create_customer(
    db: AsyncSession,
    customer_data: CustomerCreate,
)->CustomerResponse:
    
    customer = Customer(
        id=str(uuid4()),
        name=customer_data.name,
        phone_number=customer_data.phone_number,
        whatsApp_number=customer_data.whatsApp_number,
    )

    db.add(customer)

    try:
        await db.commit()
        await db.refresh(customer)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Phone number already exists",
        )

    return customer


async def update_customer(
    db: AsyncSession,
    customer_id: str,
    customer_data: CustomerUpdate,
)->CustomerResponse:
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )

    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    updates = customer_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(customer, field, value)

    try:
        await db.commit()
        await db.refresh(customer)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Phone number already exists",
        )

    return customer


async def delete_customer(
    db: AsyncSession,
    customer_id: str,
):
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )

    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found",
        )

    await db.delete(customer)
    await db.commit()

    return {"message":"Deleted Successfully"}