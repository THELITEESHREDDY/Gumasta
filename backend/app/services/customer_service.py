from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerNotFoundError(Exception):
    pass


class DuplicateMobileError(Exception):
    pass


class InvalidCustomerUpdateError(Exception):
    pass


async def get_customer_by_mobile(
    db: AsyncSession,
    shop_id: UUID,
    mobile: str
) -> Customer | None:

    result = await db.execute(
        select(Customer).where(
            Customer.shop_id == shop_id,
            Customer.mobile == mobile
        )
    )

    return result.scalar_one_or_none()


async def create_customer(
    db: AsyncSession,
    shop_id: UUID,
    data: CustomerCreate
) -> Customer:

    existing_customer = await get_customer_by_mobile(
        db, shop_id, data.mobile
    )

    if existing_customer:
        raise DuplicateMobileError(
            "Mobile number already registered in this shop"
        )

    customer = Customer(
        shop_id=shop_id,
        **data.model_dump()
    )

    db.add(customer)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        if await get_customer_by_mobile(
            db, shop_id, data.mobile
        ):
            raise DuplicateMobileError(
                "Mobile number already registered in this shop"
            )

        raise

    await db.refresh(customer)

    return customer


async def get_customers(
    db: AsyncSession,
    shop_id: UUID,
    search: str | None = None
) -> list[Customer]:

    query = select(Customer).where(
        Customer.shop_id == shop_id
    )

    if search and search.strip():

        search = search.strip()

        query = query.where(
            or_(
                Customer.name.icontains(search, autoescape=True),
                Customer.mobile.contains(search, autoescape=True),
                Customer.alternate_mobile.contains(
                    search, autoescape=True
                )
            )
        )

    query = query.order_by(Customer.name)

    result = await db.execute(query)

    return list(result.scalars().all())


async def get_customer(
    db: AsyncSession,
    shop_id: UUID,
    customer_id: UUID
) -> Customer:

    result = await db.execute(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.shop_id == shop_id
        )
    )

    customer = result.scalar_one_or_none()

    if customer is None:
        raise CustomerNotFoundError()

    return customer


async def update_customer(
    db: AsyncSession,
    shop_id: UUID,
    customer_id: UUID,
    data: CustomerUpdate
) -> Customer:

    customer = await get_customer(
        db, shop_id, customer_id
    )

    updates = data.model_dump(exclude_unset=True)

    for field in ("name", "mobile"):
        if field in updates and updates[field] is None:
            raise InvalidCustomerUpdateError(
                f"{field} cannot be null"
            )

    new_mobile = updates.get("mobile", customer.mobile)

    if new_mobile != customer.mobile:

        existing_customer = await get_customer_by_mobile(
            db, shop_id, new_mobile
        )

        if existing_customer:
            raise DuplicateMobileError(
                "Mobile number already registered in this shop"
            )

    for field, value in updates.items():
        setattr(customer, field, value)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        existing_customer = await get_customer_by_mobile(
            db, shop_id, new_mobile
        )

        if existing_customer and existing_customer.id != customer_id:
            raise DuplicateMobileError(
                "Mobile number already registered in this shop"
            )

        raise

    await db.refresh(customer)

    return customer