import asyncio
from decimal import Decimal
import pytest

from httpx import AsyncClient, ASGITransport

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker
)

from app.main import app as fastapi_app
from app.db.base import Base
from app.db.session import get_db

import app.models


@pytest.fixture
async def concurrent_client(tmp_path):

    db_path = tmp_path / "concurrency.db"

    engine = create_async_engine(
        f"sqlite+aiosqlite:///{db_path.as_posix()}",
        connect_args={"timeout": 10}
    )

    @event.listens_for(engine.sync_engine, "connect")
    def configure_sqlite(dbapi_connection, connection_record):

        cursor = dbapi_connection.cursor()

        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=10000")

        cursor.close()

    TestSessionLocal = async_sessionmaker(
        bind=engine,
        expire_on_commit=False
    )

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    try:

        async with AsyncClient(
            transport=ASGITransport(app=fastapi_app),
            base_url="http://test"
        ) as client:

            yield client

    finally:

        fastapi_app.dependency_overrides.pop(get_db, None)

        await engine.dispose()

async def test_concurrent_database_connection(
    concurrent_client
):

    responses = await asyncio.gather(
        concurrent_client.get("/health/db"),
        concurrent_client.get("/health/db"),
        concurrent_client.get("/health/db")
    )

    assert all(
        response.status_code == 200
        for response in responses
    )


@pytest.fixture
async def order_setup(concurrent_client):

    client = concurrent_client

    response = await client.post(
        "/auth/register",
        json={
            "name": "Test Owner",
            "email": "owner@example.com",
            "mobile": "9876543210",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 201

    response = await client.post(
        "/auth/login",
        data={
            "username": "owner@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 200

    headers = {
        "Authorization": f"Bearer {response.json()['access_token']}"
    }

    response = await client.post(
        "/shops",
        json={
            "name": "Test Kirana Store",
            "address": "Main Road",
            "contact": "9876543210"
        },
        headers=headers
    )

    assert response.status_code == 201

    shop_id = response.json()["id"]

    response = await client.post(
        f"/shops/{shop_id}/customers",
        json={
            "name": "Test Customer",
            "mobile": "9999999999"
        },
        headers=headers
    )

    assert response.status_code == 201

    customer_id = response.json()["id"]

    response = await client.post(
        f"/shops/{shop_id}/products",
        json={
            "name": "Rice",
            "cost_price": "40.00",
            "selling_price": "50.00",
            "unit": "kg",
            "stock_quantity": 100
        },
        headers=headers
    )

    assert response.status_code == 201

    product_id = response.json()["id"]

    return {
        "headers": headers,
        "shop_id": shop_id,
        "customer_id": customer_id,
        "product_id": product_id
    }


async def test_concurrent_orders_prevent_overselling(
    concurrent_client,
    order_setup
):

    client = concurrent_client

    headers = order_setup["headers"]
    shop_id = order_setup["shop_id"]
    customer_id = order_setup["customer_id"]
    product_id = order_setup["product_id"]

    order_url = f"/shops/{shop_id}/orders"

    order_data = {
        "customer_id": customer_id,
        "order_items": [
            {
                "product_id": product_id,
                "quantity": 70
            }
        ]
    }

    # Submit two orders concurrently.
    responses = await asyncio.gather(
        client.post(
            order_url,
            json=order_data,
            headers=headers
        ),
        client.post(
            order_url,
            json=order_data,
            headers=headers
        )
    )

    statuses = sorted(
        response.status_code
        for response in responses
    )

    assert statuses == [201, 409]

    # Verify remaining stock.
    response = await client.get(
        f"/shops/{shop_id}/products/{product_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 30

    # Verify only one order was persisted.
    response = await client.get(
        order_url,
        headers=headers
    )

    assert response.status_code == 200

    orders = response.json()

    assert len(orders) == 1

    assert Decimal(
        orders[0]["total_amount"]
    ) == Decimal("3500.00")

@pytest.fixture
async def payment_setup(concurrent_client, order_setup):

    shop_id = order_setup["shop_id"]
    headers = order_setup["headers"]

    response = await concurrent_client.post(
        f"/shops/{shop_id}/orders",
        json={
            "customer_id": order_setup["customer_id"],
            "order_items": [
                {
                    "product_id": order_setup["product_id"],
                    "quantity": 20
                }
            ]
        },
        headers=headers
    )

    assert response.status_code == 201, response.text

    order = response.json()

    assert Decimal(
        order["total_amount"]
    ) == Decimal("1000.00")

    return {
        **order_setup,
        "order_id": order["id"]
    }

async def test_concurrent_payments_prevent_overpayment(
    concurrent_client,
    payment_setup
):

    client = concurrent_client

    headers = payment_setup["headers"]
    shop_id = payment_setup["shop_id"]
    order_id = payment_setup["order_id"]

    order_url = f"/shops/{shop_id}/orders/{order_id}"
    payment_url = f"{order_url}/payments"

    payment_data = {
        "amount": "700.00",
        "payment_method": "cash"
    }

    responses = await asyncio.gather(
        client.post(
            payment_url,
            json=payment_data,
            headers=headers
        ),
        client.post(
            payment_url,
            json=payment_data,
            headers=headers
        )
    )

    statuses = sorted(
        response.status_code
        for response in responses
    )

    assert statuses == [201, 409]

    # Verify outstanding balance.
    response = await client.get(
        f"{order_url}/payment-summary",
        headers=headers
    )

    assert response.status_code == 200

    summary = response.json()

    assert Decimal(
        summary["amount_paid"]
    ) == Decimal("700.00")

    assert Decimal(
        summary["amount_due"]
    ) == Decimal("300.00")

    assert summary["payment_status"] == "partially_paid"

    # Verify only one payment was persisted.
    response = await client.get(
        payment_url,
        headers=headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_concurrent_cancellation_restores_stock_once(
    concurrent_client,
    payment_setup
):

    client = concurrent_client

    headers = payment_setup["headers"]
    shop_id = payment_setup["shop_id"]
    order_id = payment_setup["order_id"]
    product_id = payment_setup["product_id"]

    order_url = f"/shops/{shop_id}/orders/{order_id}"
    product_url = f"/shops/{shop_id}/products/{product_id}"

    # Verify initial stock after order creation.
    response = await client.get(
        product_url,
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 80

    # Submit two cancellation requests concurrently.
    responses = await asyncio.gather(
        client.post(
            f"{order_url}/cancel",
            headers=headers
        ),
        client.post(
            f"{order_url}/cancel",
            headers=headers
        )
    )

    statuses = sorted(
        response.status_code
        for response in responses
    )

    assert statuses == [200, 409]

    # Verify stock was restored exactly once.
    response = await client.get(
        product_url,
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 100

    # Verify final order status.
    response = await client.get(
        order_url,
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

async def test_concurrent_payment_and_cancellation(
    concurrent_client,
    payment_setup
):

    client = concurrent_client

    headers = payment_setup["headers"]
    shop_id = payment_setup["shop_id"]
    order_id = payment_setup["order_id"]
    product_id = payment_setup["product_id"]

    order_url = f"/shops/{shop_id}/orders/{order_id}"
    product_url = f"/shops/{shop_id}/products/{product_id}"

    # Execute both operations concurrently.
    payment_response, cancel_response = await asyncio.gather(
        client.post(
            f"{order_url}/payments",
            json={
                "amount": "400.00",
                "payment_method": "cash"
            },
            headers=headers
        ),
        client.post(
            f"{order_url}/cancel",
            headers=headers
        )
    )

    # Only one operation should succeed.
    assert (
        payment_response.status_code,
        cancel_response.status_code
    ) in [
        (201, 409),
        (409, 200)
    ]

    # Retrieve final order state.
    response = await client.get(
        order_url,
        headers=headers
    )

    assert response.status_code == 200
    order = response.json()

    # Retrieve final stock.
    response = await client.get(
        product_url,
        headers=headers
    )

    assert response.status_code == 200
    stock = response.json()["stock_quantity"]

    # Retrieve final payment summary.
    response = await client.get(
        f"{order_url}/payment-summary",
        headers=headers
    )

    assert response.status_code == 200
    summary = response.json()

    # Retrieve persisted payments.
    response = await client.get(
        f"{order_url}/payments",
        headers=headers
    )

    assert response.status_code == 200
    payments = response.json()

    if payment_response.status_code == 201:

        assert order["status"] == "completed"
        assert stock == 80

        assert Decimal(
            summary["amount_paid"]
        ) == Decimal("400.00")

        assert Decimal(
            summary["amount_due"]
        ) == Decimal("600.00")

        assert summary["payment_status"] == "partially_paid"
        assert len(payments) == 1

    else:

        assert order["status"] == "cancelled"
        assert stock == 100

        assert Decimal(
            summary["amount_paid"]
        ) == Decimal("0.00")

        assert Decimal(
            summary["amount_due"]
        ) == Decimal("0.00")

        assert summary["payment_status"] == "cancelled"
        assert len(payments) == 0