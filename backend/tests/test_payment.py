import pytest

from uuid import uuid4
from decimal import Decimal


@pytest.fixture
async def owner(create_authenticated_user):
    return await create_authenticated_user(
        "owner@example.com"
    )


@pytest.fixture
async def another_user(create_authenticated_user):
    return await create_authenticated_user(
        "another@example.com"
    )


@pytest.fixture
async def shop(client, owner):

    response = await client.post(
        "/shops",
        json={
            "name": "Test Shop",
            "address": "Main Road",
            "contact": "9876543210"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 201

    return response.json()


@pytest.fixture
async def customer(client, owner, shop):

    response = await client.post(
        f"/shops/{shop['id']}/customers",
        json={
            "name": "Ravi Kumar",
            "mobile": "9876543210"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 201

    return response.json()


@pytest.fixture
async def product(client, owner, shop):

    response = await client.post(
        f"/shops/{shop['id']}/products",
        json={
            "name": "Rice",
            "cost_price": "40.00",
            "selling_price": "50.00",
            "unit": "kg",
            "stock_quantity": 100
        },
        headers=owner["headers"]
    )

    assert response.status_code == 201

    return response.json()


@pytest.fixture
async def order(client, owner, shop, customer, product):

    response = await client.post(
        f"/shops/{shop['id']}/orders",
        json={
            "customer_id": customer["id"],
            "order_items": [
                {
                    "product_id": product["id"],
                    "quantity": 20
                }
            ]
        },
        headers=owner["headers"]
    )

    assert response.status_code == 201, response.text

    assert Decimal(
        response.json()["total_amount"]
    ) == Decimal("1000.00")

    return response.json()


@pytest.fixture
def order_url(shop, order):
    return f"/shops/{shop['id']}/orders/{order['id']}"


@pytest.fixture
def payment_url(order_url):
    return f"{order_url}/payments"


@pytest.fixture
def summary_url(order_url):
    return f"{order_url}/payment-summary"


@pytest.fixture
def payment_data():
    return {
        "amount": "400.00",
        "payment_method": "upi",
        "reference": "UPI123456"
    }


@pytest.fixture
async def created_payment(
    client, owner, payment_url, payment_data
):

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201, response.text

    return response.json()

async def test_create_payment(created_payment, order):

    assert created_payment["order_id"] == order["id"]

    assert Decimal(
        created_payment["amount"]
    ) == Decimal("400.00")

    assert created_payment["payment_method"] == "upi"
    assert created_payment["reference"] == "UPI123456"


@pytest.mark.parametrize(
    "method",
    ["cash", "upi", "bank_transfer", "card"]
)
async def test_supported_payment_methods(
    client, owner, payment_url, payment_data, method
):

    payment_data["payment_method"] = method

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201
    assert response.json()["payment_method"] == method


async def test_payment_without_reference(
    client, owner, payment_url, payment_data
):

    payment_data.pop("reference")

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201
    assert response.json()["reference"] is None

async def test_unpaid_order_summary(
    client, owner, summary_url
):

    response = await client.get(
        summary_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200

    summary = response.json()

    assert Decimal(summary["total_amount"]) == Decimal("1000")
    assert Decimal(summary["amount_paid"]) == Decimal("0")
    assert Decimal(summary["amount_due"]) == Decimal("1000")
    assert summary["payment_status"] == "unpaid"


async def test_partial_payment_summary(
    client, owner, summary_url, created_payment
):

    response = await client.get(
        summary_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200

    summary = response.json()

    assert Decimal(summary["amount_paid"]) == Decimal("400")
    assert Decimal(summary["amount_due"]) == Decimal("600")
    assert summary["payment_status"] == "partially_paid"


async def test_full_payment_summary(
    client, owner, payment_url, summary_url, payment_data
):

    payment_data["amount"] = "1000.00"

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201

    response = await client.get(
        summary_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200

    summary = response.json()

    assert Decimal(summary["amount_paid"]) == Decimal("1000")
    assert Decimal(summary["amount_due"]) == Decimal("0")
    assert summary["payment_status"] == "paid"


async def test_multiple_partial_payments(
    client, owner, payment_url, summary_url
):

    for amount in ["400.00", "350.00", "250.00"]:

        response = await client.post(
            payment_url,
            json={
                "amount": amount,
                "payment_method": "cash"
            },
            headers=owner["headers"]
        )

        assert response.status_code == 201

    response = await client.get(
        summary_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200

    summary = response.json()

    assert Decimal(summary["amount_paid"]) == Decimal("1000")
    assert Decimal(summary["amount_due"]) == Decimal("0")
    assert summary["payment_status"] == "paid"

async def test_reject_overpayment(
    client, owner, payment_url, payment_data
):

    payment_data["amount"] = "1000.01"

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 409


async def test_reject_overpayment_after_partial_payment(
    client, owner, payment_url,
    payment_data, created_payment
):

    payment_data["amount"] = "600.01"

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 409


async def test_reject_payment_after_full_payment(
    client, owner, payment_url, payment_data
):

    payment_data["amount"] = "1000.00"

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201

    payment_data["amount"] = "1.00"

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 409


async def test_failed_payment_preserves_balance(
    client, owner, payment_url,
    summary_url, created_payment
):

    response = await client.post(
        payment_url,
        json={
            "amount": "700.00",
            "payment_method": "cash"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 409

    response = await client.get(
        summary_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200

    summary = response.json()

    assert Decimal(summary["amount_paid"]) == Decimal("400")
    assert Decimal(summary["amount_due"]) == Decimal("600")

    response = await client.get(
        payment_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

@pytest.mark.parametrize(
    "amount",
    ["0.00", "-100.00", "10.123", "invalid"]
)
async def test_invalid_payment_amount(
    client, owner, payment_url, payment_data, amount
):

    payment_data["amount"] = amount

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_invalid_payment_method(
    client, owner, payment_url, payment_data
):

    payment_data["payment_method"] = "invalid"

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_missing_payment_amount(
    client, owner, payment_url, payment_data
):

    payment_data.pop("amount")

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_invalid_payment_reference(
    client, owner, payment_url, payment_data
):

    payment_data["reference"] = "A" * 256

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422

async def test_list_empty_payments(
    client, owner, payment_url
):

    response = await client.get(
        payment_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_list_payments(
    client, owner, payment_url, created_payment
):

    response = await client.get(
        payment_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200

    payments = response.json()

    assert len(payments) == 1
    assert payments[0]["id"] == created_payment["id"]


async def test_list_multiple_payments(
    client, owner, payment_url
):

    payment_ids = []

    for amount in ["200.00", "300.00"]:

        response = await client.post(
            payment_url,
            json={
                "amount": amount,
                "payment_method": "cash"
            },
            headers=owner["headers"]
        )

        assert response.status_code == 201

        payment_ids.append(response.json()["id"])

    response = await client.get(
        payment_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200

    payments = response.json()

    assert len(payments) == 2

    assert {
        payment["id"] for payment in payments
    } == set(payment_ids)


async def test_cannot_pay_cancelled_order(
    client, owner, order_url, payment_url, payment_data
):

    response = await client.post(
        f"{order_url}/cancel",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    response = await client.post(
        payment_url,
        json=payment_data,
        headers=owner["headers"]
    )

    assert response.status_code == 409


async def test_cannot_cancel_partially_paid_order(
    client, owner, order_url, created_payment
):

    response = await client.post(
        f"{order_url}/cancel",
        headers=owner["headers"]
    )

    assert response.status_code == 409


async def test_cannot_cancel_fully_paid_order(
    client, owner, order_url, payment_url
):

    response = await client.post(
        payment_url,
        json={
            "amount": "1000.00",
            "payment_method": "cash"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 201

    response = await client.post(
        f"{order_url}/cancel",
        headers=owner["headers"]
    )

    assert response.status_code == 409


async def test_failed_cancellation_preserves_stock(
    client, owner, shop, product,
    order_url, created_payment
):

    response = await client.post(
        f"{order_url}/cancel",
        headers=owner["headers"]
    )

    assert response.status_code == 409

    response = await client.get(
        f"/shops/{shop['id']}/products/{product['id']}",
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 80

    response = await client.get(
        order_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


async def test_cancelled_order_payment_summary(
    client, owner, order_url, summary_url
):

    response = await client.post(
        f"{order_url}/cancel",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    response = await client.get(
        summary_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200

    summary = response.json()

    assert Decimal(summary["total_amount"]) == Decimal("1000")
    assert Decimal(summary["amount_paid"]) == Decimal("0")
    assert Decimal(summary["amount_due"]) == Decimal("0")
    assert summary["payment_status"] == "cancelled"


@pytest.mark.parametrize(
    "method,suffix",
    [
        ("POST", "/payments"),
        ("GET", "/payments"),
        ("GET", "/payment-summary")
    ]
)
async def test_payment_requires_authentication(
    client, order_url, payment_data, method, suffix
):

    response = await client.request(
        method,
        f"{order_url}{suffix}",
        json=payment_data if method == "POST" else None
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "method,suffix",
    [
        ("POST", "/payments"),
        ("GET", "/payments"),
        ("GET", "/payment-summary")
    ]
)
async def test_cross_user_payment_access(
    client, another_user, order_url,
    payment_data, method, suffix
):

    response = await client.request(
        method,
        f"{order_url}{suffix}",
        json=payment_data if method == "POST" else None,
        headers=another_user["headers"]
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "method,suffix",
    [
        ("POST", "/payments"),
        ("GET", "/payments"),
        ("GET", "/payment-summary")
    ]
)
async def test_payment_order_not_found(
    client, owner, shop, payment_data, method, suffix
):

    url = f"/shops/{shop['id']}/orders/{uuid4()}{suffix}"

    response = await client.request(
        method,
        url,
        json=payment_data if method == "POST" else None,
        headers=owner["headers"]
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "method,suffix",
    [
        ("POST", "/payments"),
        ("GET", "/payments"),
        ("GET", "/payment-summary")
    ]
)
async def test_cross_shop_payment_access(
    client, owner, order, payment_data, method, suffix
):

    response = await client.post(
        "/shops",
        json={
            "name": "Second Shop",
            "address": "Another Road",
            "contact": "9999999999"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 201

    second_shop = response.json()

    url = (
        f"/shops/{second_shop['id']}/orders/"
        f"{order['id']}{suffix}"
    )

    response = await client.request(
        method,
        url,
        json=payment_data if method == "POST" else None,
        headers=owner["headers"]
    )

    assert response.status_code == 404