import pytest

from decimal import Decimal
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4
from uuid import UUID
from sqlalchemy import update

from app.main import app as fastapi_app
from app.db.session import get_db
from app.models.order import Order
from app.models.payments import Payment

from app.services.dashboard_service import resolve_date_range


IST = timezone(timedelta(hours=5, minutes=30))


@pytest.fixture
async def owner(create_authenticated_user):
    return await create_authenticated_user(
        "dashboard-owner@example.com"
    )


@pytest.fixture
async def another_user(create_authenticated_user):
    return await create_authenticated_user(
        "another-owner@example.com"
    )


@pytest.fixture
async def shop(client, owner):
    response = await client.post(
        "/shops",
        headers=owner["headers"],
        json={
            "name": "Test Kirana Store",
            "address": "Main Road",
            "contact": "9876543210"
        }
    )

    assert response.status_code == 201
    return response.json()


@pytest.fixture
def dashboard_url(shop):
    return f"/shops/{shop['id']}/dashboard"


@pytest.fixture
async def customer(client, owner, shop):
    response = await client.post(
        f"/shops/{shop['id']}/customers",
        headers=owner["headers"],
        json={
            "name": "Ravi Kumar",
            "mobile": "9876543210",
            "alternate_mobile": "9123456780"
        }
    )

    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def product(client, owner, shop):
    response = await client.post(
        f"/shops/{shop['id']}/products",
        headers=owner["headers"],
        json={
            "name": "Rice",
            "cost_price": "40.00",
            "selling_price": "50.00",
            "stock_quantity": 100,
            "unit": "kg"
        }
    )

    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def create_order(
    client, owner, shop, customer, product
):
    async def _create_order(quantity=20):

        response = await client.post(
            f"/shops/{shop['id']}/orders",
            headers=owner["headers"],
            json={
                "customer_id": customer["id"],
                "order_items": [
                    {
                        "product_id": product["id"],
                        "quantity": quantity
                    }
                ]
            }
        )

        assert response.status_code == 201
        return response.json()

    return _create_order


@pytest.fixture
async def create_payment(client, owner, shop):

    async def _create_payment(order_id, amount):

        response = await client.post(
            f"/shops/{shop['id']}/orders/{order_id}/payments",
            headers=owner["headers"],
            json={
                "amount": str(amount),
                "payment_method": "cash"
            }
        )

        assert response.status_code == 201
        return response.json()

    return _create_payment


async def test_empty_dashboard_summary(
    client, owner, dashboard_url
):
    response = await client.get(
        f"{dashboard_url}/summary",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_sales"]) == 0
    assert Decimal(data["amount_received"]) == 0
    assert Decimal(data["outstanding_amount"]) == 0
    assert data["total_orders"] == 0


async def test_summary_with_unpaid_order(
    client, owner, dashboard_url, create_order
):
    await create_order(quantity=20)

    response = await client.get(
        f"{dashboard_url}/summary",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_sales"]) == 1000
    assert Decimal(data["amount_received"]) == 0
    assert Decimal(data["outstanding_amount"]) == 1000
    assert data["total_orders"] == 1


async def test_summary_with_partial_payment(
    client, owner, dashboard_url,
    create_order, create_payment
):
    order = await create_order(quantity=20)

    await create_payment(order["id"], 400)

    response = await client.get(
        f"{dashboard_url}/summary",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_sales"]) == 1000
    assert Decimal(data["amount_received"]) == 400
    assert Decimal(data["outstanding_amount"]) == 600
    assert data["total_orders"] == 1


async def test_summary_with_multiple_payments(
    client, owner, dashboard_url,
    create_order, create_payment
):
    order = await create_order(quantity=20)

    await create_payment(order["id"], 300)
    await create_payment(order["id"], 200)

    response = await client.get(
        f"{dashboard_url}/summary",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_sales"]) == 1000
    assert Decimal(data["amount_received"]) == 500
    assert Decimal(data["outstanding_amount"]) == 500
    assert data["total_orders"] == 1

async def test_summary_with_multiple_orders(
    client, owner, dashboard_url,
    create_order, create_payment
):
    order1 = await create_order(quantity=20)
    order2 = await create_order(quantity=10)

    await create_payment(order1["id"], 400)
    await create_payment(order2["id"], 500)

    response = await client.get(
        f"{dashboard_url}/summary",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_sales"]) == 1500
    assert Decimal(data["amount_received"]) == 900
    assert Decimal(data["outstanding_amount"]) == 600
    assert data["total_orders"] == 2

async def test_summary_excludes_cancelled_orders(
    client, owner, shop,
    dashboard_url, create_order
):
    order = await create_order(quantity=20)

    cancel_response = await client.post(
        f"/shops/{shop['id']}/orders/{order['id']}/cancel",
        headers=owner["headers"]
    )

    assert cancel_response.status_code == 200

    response = await client.get(
        f"{dashboard_url}/summary",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_sales"]) == 0
    assert Decimal(data["amount_received"]) == 0
    assert Decimal(data["outstanding_amount"]) == 0
    assert data["total_orders"] == 0

async def test_outstanding_independent_of_date_range(
    client, owner, dashboard_url, create_order
):
    await create_order(quantity=20)

    yesterday = (
        datetime.now(IST).date() - timedelta(days=1)
    ).isoformat()

    response = await client.get(
        f"{dashboard_url}/summary",
        headers=owner["headers"],
        params={
            "start_date": yesterday,
            "end_date": yesterday
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_sales"]) == 0
    assert Decimal(data["amount_received"]) == 0
    assert Decimal(data["outstanding_amount"]) == 1000
    assert data["total_orders"] == 0

async def test_empty_dashboard_orders(
    client, owner, dashboard_url
):
    response = await client.get(
        f"{dashboard_url}/orders",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["limit"] == 20
    assert data["offset"] == 0


async def test_dashboard_unpaid_order(
    client, owner, dashboard_url,
    create_order, customer
):
    order = await create_order(quantity=20)

    response = await client.get(
        f"{dashboard_url}/orders",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()
    item = data["items"][0]

    assert data["total"] == 1
    assert item["order_id"] == order["id"]
    assert item["customer_id"] == customer["id"]
    assert item["customer_name"] == customer["name"]
    assert item["customer_mobile"] == customer["mobile"]

    assert Decimal(item["total_amount"]) == 1000
    assert Decimal(item["amount_paid"]) == 0
    assert Decimal(item["amount_due"]) == 1000

    assert item["order_status"] == "completed"
    assert item["payment_status"] == "unpaid"


async def test_dashboard_partially_paid_order(
    client, owner, dashboard_url,
    create_order, create_payment
):
    order = await create_order(quantity=20)

    await create_payment(order["id"], 300)
    await create_payment(order["id"], 200)

    response = await client.get(
        f"{dashboard_url}/orders",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()
    item = data["items"][0]

    assert data["total"] == 1
    assert len(data["items"]) == 1

    assert Decimal(item["total_amount"]) == 1000
    assert Decimal(item["amount_paid"]) == 500
    assert Decimal(item["amount_due"]) == 500

    assert item["payment_status"] == "partially_paid"

async def test_dashboard_fully_paid_order(
    client, owner, dashboard_url,
    create_order, create_payment
):
    order = await create_order(quantity=20)

    await create_payment(order["id"], 1000)

    response = await client.get(
        f"{dashboard_url}/orders",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    item = response.json()["items"][0]

    assert Decimal(item["amount_paid"]) == 1000
    assert Decimal(item["amount_due"]) == 0
    assert item["payment_status"] == "paid"


async def test_dashboard_cancelled_order(
    client, owner, shop,
    dashboard_url, create_order
):
    order = await create_order(quantity=20)

    response = await client.post(
        f"/shops/{shop['id']}/orders/{order['id']}/cancel",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    response = await client.get(
        f"{dashboard_url}/orders",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()
    item = data["items"][0]

    assert data["total"] == 1
    assert item["order_status"] == "cancelled"
    assert item["payment_status"] == "cancelled"

    assert Decimal(item["total_amount"]) == 1000
    assert Decimal(item["amount_due"]) == 0

@pytest.mark.parametrize(
    "search, expected_total",
    [
        ("Ravi", 1),
        ("ravi", 1),
        ("987654", 1),
        ("912345", 1),
        ("Unknown Customer", 0)
    ]
)
async def test_dashboard_order_search(
    client, owner, dashboard_url,
    create_order, search, expected_total
):
    await create_order(quantity=20)

    response = await client.get(
        f"{dashboard_url}/orders",
        headers=owner["headers"],
        params={"search": search}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == expected_total
    assert len(data["items"]) == expected_total

async def test_dashboard_orders_date_filter(
    client, owner, dashboard_url, create_order
):
    await create_order(quantity=20)

    yesterday = (
        datetime.now(IST).date() - timedelta(days=1)
    ).isoformat()

    response = await client.get(
        f"{dashboard_url}/orders",
        headers=owner["headers"],
        params={
            "start_date": yesterday,
            "end_date": yesterday
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["items"] == []


async def test_dashboard_orders_pagination(
    client, owner, dashboard_url, create_order
):
    orders = [
        await create_order(quantity=10)
        for _ in range(3)
    ]

    received_ids = []

    for offset in range(3):

        response = await client.get(
            f"{dashboard_url}/orders",
            headers=owner["headers"],
            params={
                "limit": 1,
                "offset": offset
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 3
        assert data["limit"] == 1
        assert data["offset"] == offset
        assert len(data["items"]) == 1

        received_ids.append(
            data["items"][0]["order_id"]
        )

    assert len(set(received_ids)) == 3

    assert set(received_ids) == {
        order["id"] for order in orders
    }

async def test_empty_dashboard_transactions(
    client, owner, dashboard_url
):
    response = await client.get(
        f"{dashboard_url}/transactions",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["total"] == 0
    assert data["limit"] == 20
    assert data["offset"] == 0

async def test_dashboard_transaction_details(
    client, owner, dashboard_url,
    create_order, create_payment, customer
):
    order = await create_order(quantity=20)
    payment = await create_payment(order["id"], 400)

    response = await client.get(
        f"{dashboard_url}/transactions",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()
    item = data["items"][0]

    assert data["total"] == 1
    assert item["payment_id"] == payment["id"]
    assert item["order_id"] == order["id"]

    assert item["customer_id"] == customer["id"]
    assert item["customer_name"] == customer["name"]
    assert item["customer_mobile"] == customer["mobile"]

    assert Decimal(item["amount"]) == 400
    assert item["payment_method"] == "cash"
    assert item["reference"] is None
    assert item["created_at"] is not None

async def test_dashboard_multiple_payments(
    client, owner, dashboard_url,
    create_order, create_payment
):
    order = await create_order(quantity=20)

    payment1 = await create_payment(order["id"], 300)
    payment2 = await create_payment(order["id"], 200)

    response = await client.get(
        f"{dashboard_url}/transactions",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert len(data["items"]) == 2

    assert {
        item["payment_id"] for item in data["items"]
    } == {
        payment1["id"],
        payment2["id"]
    }

    assert sum(
        Decimal(item["amount"])
        for item in data["items"]
    ) == 500

    assert all(
        item["order_id"] == order["id"]
        for item in data["items"]
    )

async def test_unpaid_order_has_no_transactions(
    client, owner, dashboard_url, create_order
):
    await create_order(quantity=20)

    response = await client.get(
        f"{dashboard_url}/transactions",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["items"] == []

@pytest.mark.parametrize(
    "search, expected_total",
    [
        ("Ravi", 1),
        ("ravi", 1),
        ("987654", 1),
        ("912345", 1),
        ("Unknown Customer", 0)
    ]
)
async def test_dashboard_transaction_search(
    client, owner, dashboard_url,
    create_order, create_payment,
    search, expected_total
):
    order = await create_order(quantity=20)

    await create_payment(order["id"], 400)

    response = await client.get(
        f"{dashboard_url}/transactions",
        headers=owner["headers"],
        params={"search": search}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == expected_total
    assert len(data["items"]) == expected_total

async def test_dashboard_transactions_date_filter(
    client, owner, dashboard_url,
    create_order, create_payment
):
    order = await create_order(quantity=20)

    await create_payment(order["id"], 400)

    yesterday = (
        datetime.now(IST).date() - timedelta(days=1)
    ).isoformat()

    response = await client.get(
        f"{dashboard_url}/transactions",
        headers=owner["headers"],
        params={
            "start_date": yesterday,
            "end_date": yesterday
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["items"] == []

async def test_dashboard_transactions_pagination(
    client, owner, dashboard_url,
    create_order, create_payment
):
    order = await create_order(quantity=20)

    payments = [
        await create_payment(order["id"], amount)
        for amount in [100, 200, 300]
    ]

    received_ids = []

    for offset in range(3):

        response = await client.get(
            f"{dashboard_url}/transactions",
            headers=owner["headers"],
            params={
                "limit": 1,
                "offset": offset
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 3
        assert data["limit"] == 1
        assert data["offset"] == offset
        assert len(data["items"]) == 1

        received_ids.append(
            data["items"][0]["payment_id"]
        )

    assert len(set(received_ids)) == 3

    assert set(received_ids) == {
        payment["id"] for payment in payments
    }

def test_ist_date_range_conversion():

    selected_date = date(2026, 11, 25)

    _, _, start, end = resolve_date_range(
        selected_date,
        selected_date
    )

    assert start == datetime(
        2026, 11, 24, 18, 30,
        tzinfo=timezone.utc
    )

    assert end == datetime(
        2026, 11, 25, 18, 30,
        tzinfo=timezone.utc
    )

@pytest.fixture
def update_created_at(client):

    async def _update_created_at(model, record_id, timestamp):

        override = fastapi_app.dependency_overrides[get_db]

        async for db in override():

            await db.execute(
                update(model)
                .where(model.id == UUID(record_id))
                .values(created_at=timestamp)
            )

            await db.commit()

    return _update_created_at


@pytest.mark.parametrize(
    "timestamp, expected_count",
    [
        (
            datetime(2026, 11, 24, 18, 29, 59,
                     tzinfo=timezone.utc),
            0
        ),
        (
            datetime(2026, 11, 24, 18, 30, 0,
                     tzinfo=timezone.utc),
            1
        ),
        (
            datetime(2026, 11, 25, 18, 29, 59,
                     tzinfo=timezone.utc),
            1
        ),
        (
            datetime(2026, 11, 25, 18, 30, 0,
                     tzinfo=timezone.utc),
            0
        )
    ]
)
async def test_dashboard_ist_order_boundaries(
    client, owner, dashboard_url,
    create_order, update_created_at,
    timestamp, expected_count
):
    order = await create_order(quantity=20)

    await update_created_at(
        Order, order["id"], timestamp
    )

    params = {
        "start_date": "2026-11-25",
        "end_date": "2026-11-25"
    }

    response = await client.get(
        f"{dashboard_url}/orders",
        headers=owner["headers"],
        params=params
    )

    assert response.status_code == 200
    assert response.json()["total"] == expected_count

    response = await client.get(
        f"{dashboard_url}/summary",
        headers=owner["headers"],
        params=params
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_orders"] == expected_count
    assert Decimal(data["total_sales"]) == 1000 * expected_count


async def test_payment_received_against_older_order(
    client, owner, dashboard_url,
    create_order, create_payment,
    update_created_at
):
    order = await create_order(quantity=20)

    payment = await create_payment(order["id"], 400)

    await update_created_at(
        Order,
        order["id"],
        datetime(2026, 11, 24, 10, 0,
                 tzinfo=timezone.utc)
    )

    await update_created_at(
        Payment,
        payment["id"],
        datetime(2026, 11, 25, 10, 0,
                 tzinfo=timezone.utc)
    )

    params = {
        "start_date": "2026-11-25",
        "end_date": "2026-11-25"
    }

    response = await client.get(
        f"{dashboard_url}/summary",
        headers=owner["headers"],
        params=params
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_sales"]) == 0
    assert Decimal(data["amount_received"]) == 400
    assert Decimal(data["outstanding_amount"]) == 600
    assert data["total_orders"] == 0

    response = await client.get(
        f"{dashboard_url}/orders",
        headers=owner["headers"],
        params=params
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0

    response = await client.get(
        f"{dashboard_url}/transactions",
        headers=owner["headers"],
        params=params
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["payment_id"] == payment["id"]
    assert Decimal(data["items"][0]["amount"]) == 400

@pytest.mark.parametrize(
    "endpoint",
    ["summary", "orders", "transactions"]
)
async def test_dashboard_invalid_date_range(
    client, owner, dashboard_url, endpoint
):
    response = await client.get(
        f"{dashboard_url}/{endpoint}",
        headers=owner["headers"],
        params={
            "start_date": "2026-11-25",
            "end_date": "2026-11-24"
        }
    )

    assert response.status_code == 422

@pytest.mark.parametrize(
    "endpoint",
    ["summary", "orders", "transactions"]
)
async def test_dashboard_invalid_date_format(
    client, owner, dashboard_url, endpoint
):
    response = await client.get(
        f"{dashboard_url}/{endpoint}",
        headers=owner["headers"],
        params={"start_date": "invalid-date"}
    )

    assert response.status_code == 422

@pytest.mark.parametrize(
    "endpoint",
    ["orders", "transactions"]
)
@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1}
    ]
)
async def test_dashboard_invalid_pagination(
    client, owner, dashboard_url,
    endpoint, params
):
    response = await client.get(
        f"{dashboard_url}/{endpoint}",
        headers=owner["headers"],
        params=params
    )

    assert response.status_code == 422

@pytest.mark.parametrize(
    "endpoint",
    ["orders", "transactions"]
)
async def test_dashboard_offset_beyond_records(
    client, owner, dashboard_url,
    create_order, create_payment, endpoint
):
    order = await create_order(quantity=20)
    await create_payment(order["id"], 400)

    response = await client.get(
        f"{dashboard_url}/{endpoint}",
        headers=owner["headers"],
        params={"offset": 100}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"] == []
    assert data["offset"] == 100

@pytest.mark.parametrize(
    "endpoint",
    ["summary", "orders", "transactions"]
)
async def test_dashboard_requires_authentication(
    client, dashboard_url, endpoint
):
    response = await client.get(
        f"{dashboard_url}/{endpoint}"
    )

    assert response.status_code == 401

@pytest.mark.parametrize(
    "endpoint",
    ["summary", "orders", "transactions"]
)
async def test_dashboard_nonexistent_shop(
    client, owner, endpoint
):
    response = await client.get(
        f"/shops/{uuid4()}/dashboard/{endpoint}",
        headers=owner["headers"]
    )

    assert response.status_code == 404

@pytest.mark.parametrize(
    "endpoint",
    ["summary", "orders", "transactions"]
)
async def test_dashboard_unauthorized_shop_access(
    client, another_user, dashboard_url,
    create_order, create_payment, endpoint
):
    order = await create_order(quantity=20)
    await create_payment(order["id"], 400)

    response = await client.get(
        f"{dashboard_url}/{endpoint}",
        headers=another_user["headers"]
    )

    assert response.status_code == 404

async def test_dashboard_data_isolation(
    client, owner, dashboard_url,
    create_order, create_payment
):
    order = await create_order(quantity=20)
    await create_payment(order["id"], 400)

    response = await client.post(
        "/shops",
        headers=owner["headers"],
        json={
            "name": "Second Kirana Store",
            "address": "Second Main Road",
            "contact": "9876543211"
        }
    )

    assert response.status_code == 201

    second_shop = response.json()

    second_dashboard_url = (
        f"/shops/{second_shop['id']}/dashboard"
    )

    # Second shop summary must be empty.
    response = await client.get(
        f"{second_dashboard_url}/summary",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_sales"]) == 0
    assert Decimal(data["amount_received"]) == 0
    assert Decimal(data["outstanding_amount"]) == 0
    assert data["total_orders"] == 0

    # Second shop orders and transactions must be empty.
    for endpoint in ["orders", "transactions"]:

        response = await client.get(
            f"{second_dashboard_url}/{endpoint}",
            headers=owner["headers"]
        )

        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert response.json()["items"] == []

    # First shop data must remain intact.
    response = await client.get(
        f"{dashboard_url}/summary",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert Decimal(data["total_sales"]) == 1000
    assert Decimal(data["amount_received"]) == 400
    assert Decimal(data["outstanding_amount"]) == 600
    assert data["total_orders"] == 1