import pytest

from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone, timedelta


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
async def create_shop(client):

    async def create(headers):

        response = await client.post(
            "/shops",
            json={
                "name": "Test Shop",
                "address": "Main Road",
                "contact": "9876543210"
            },
            headers=headers
        )

        assert response.status_code == 201

        return response.json()

    return create


@pytest.fixture
async def shop(create_shop, owner):
    return await create_shop(owner["headers"])


@pytest.fixture
def order_url(shop):
    return f"/shops/{shop['id']}/orders"


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
async def products(client, owner, shop):

    product_data = [
        {
            "name": "Rice",
            "cost_price": "45.00",
            "selling_price": "55.00",
            "unit": "kg",
            "stock_quantity": 100
        },
        {
            "name": "Wheat",
            "cost_price": "30.00",
            "selling_price": "40.00",
            "unit": "kg",
            "stock_quantity": 50
        }
    ]

    result = []

    for data in product_data:

        response = await client.post(
            f"/shops/{shop['id']}/products",
            json=data,
            headers=owner["headers"]
        )

        assert response.status_code == 201

        result.append(response.json())

    return result


@pytest.fixture
def order_data(customer, products):

    return {
        "customer_id": customer["id"],
        "order_items": [
            {
                "product_id": products[0]["id"],
                "quantity": 10
            },
            {
                "product_id": products[1]["id"],
                "quantity": 5
            }
        ]
    }


@pytest.fixture
async def created_order(
    client, owner, order_url, order_data
):

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201, response.text

    return response.json()

async def get_stock(client, headers, shop_id, product_id):

    response = await client.get(
        f"/shops/{shop_id}/products/{product_id}",
        headers=headers
    )

    assert response.status_code == 200

    return response.json()["stock_quantity"]


async def test_create_order(
    created_order, customer, shop
):

    assert created_order["customer_id"] == customer["id"]
    assert created_order["shop_id"] == shop["id"]
    assert created_order["status"] == "completed"

    assert len(created_order["order_items"]) == 2

    assert Decimal(
        created_order["total_amount"]
    ) == Decimal("750.00")


async def test_order_deducts_stock(
    client, owner, shop, products, created_order
):

    rice_stock = await get_stock(
        client, owner["headers"],
        shop["id"], products[0]["id"]
    )

    wheat_stock = await get_stock(
        client, owner["headers"],
        shop["id"], products[1]["id"]
    )

    assert rice_stock == 90
    assert wheat_stock == 45


async def test_order_with_custom_selling_price(
    client, owner, order_url, order_data
):

    order_data["order_items"][0]["unit_price"] = "50.00"

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201

    assert Decimal(
        response.json()["total_amount"]
    ) == Decimal("700.00")


async def test_order_with_zero_selling_price(
    client, owner, order_url, order_data
):

    order_data["order_items"][0]["unit_price"] = "0.00"

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201

    assert Decimal(
        response.json()["total_amount"]
    ) == Decimal("200.00")


async def test_order_item_subtotals(created_order):

    items = {
        item["product_name"]: item
        for item in created_order["order_items"]
    }

    assert Decimal(
        items["Rice"]["subtotal"]
    ) == Decimal("550.00")

    assert Decimal(
        items["Wheat"]["subtotal"]
    ) == Decimal("200.00")


async def test_order_consumes_entire_stock(
    client, owner, shop, products,
    order_url, order_data
):

    order_data["order_items"][0]["quantity"] = 100

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201

    stock = await get_stock(
        client, owner["headers"],
        shop["id"], products[0]["id"]
    )

    assert stock == 0


async def test_order_without_items(
    client, owner, order_url, order_data
):

    order_data["order_items"] = []

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


@pytest.mark.parametrize("quantity", [0, -1, -10])
async def test_invalid_order_quantity(
    client, owner, order_url, order_data, quantity
):

    order_data["order_items"][0]["quantity"] = quantity

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_duplicate_products(
    client, owner, order_url, order_data
):

    order_data["order_items"].append(
        order_data["order_items"][0].copy()
    )

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_negative_unit_price(
    client, owner, order_url, order_data
):

    order_data["order_items"][0]["unit_price"] = "-10.00"

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_invalid_customer(
    client, owner, order_url, order_data
):

    order_data["customer_id"] = str(uuid4())

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_invalid_product(
    client, owner, order_url, order_data
):

    order_data["order_items"][0]["product_id"] = str(uuid4())

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_cannot_order_inactive_product(
    client, owner, shop, products,
    order_url, order_data
):

    response = await client.delete(
        f"/shops/{shop['id']}/products/{products[0]['id']}",
        headers=owner["headers"]
    )

    assert response.status_code == 204

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422

async def test_insufficient_stock(
    client, owner, order_url, order_data
):

    order_data["order_items"][0]["quantity"] = 101

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 409


async def test_order_transaction_rollback(
    client, owner, shop, products,
    order_url, order_data
):

    # Match the service's product processing order.
    items = sorted(
        order_data["order_items"],
        key=lambda item: item["product_id"]
    )

    items[0]["quantity"] = 1
    items[1]["quantity"] = 1000

    order_data["order_items"] = items

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 409

    # Both products must retain their original stock.
    for product in products:

        stock = await get_stock(
            client,
            owner["headers"],
            shop["id"],
            product["id"]
        )

        assert stock == product["stock_quantity"]

    # No partially created order should exist.
    response = await client.get(
        order_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_order_preserves_product_snapshot(
    client, owner, shop, products,
    order_url, created_order
):

    response = await client.patch(
        f"/shops/{shop['id']}/products/{products[0]['id']}",
        json={
            "name": "Premium Rice",
            "selling_price": "80.00"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 200

    response = await client.get(
        f"{order_url}/{created_order['id']}",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    order = response.json()

    rice_item = next(
        item for item in order["order_items"]
        if item["product_id"] == products[0]["id"]
    )

    assert rice_item["product_name"] == "Rice"

    assert Decimal(
        rice_item["unit_price"]
    ) == Decimal("55.00")

    assert Decimal(
        order["total_amount"]
    ) == Decimal("750.00")


async def test_get_order(
    client, owner, order_url, created_order
):

    response = await client.get(
        f"{order_url}/{created_order['id']}",
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["id"] == created_order["id"]
    assert len(response.json()["order_items"]) == 2


async def test_list_orders(
    client, owner, order_url, created_order
):

    response = await client.get(
        order_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == created_order["id"]


async def test_filter_orders_by_customer(
    client, owner, order_url, customer, created_order
):

    response = await client.get(
        order_url,
        params={"customer_id": customer["id"]},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get(
        order_url,
        params={"customer_id": str(uuid4())},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_filter_orders_by_status(
    client, owner, order_url, created_order
):

    response = await client.get(
        order_url,
        params={"status": "completed"},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get(
        order_url,
        params={"status": "cancelled"},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_filter_orders_by_date(
    client, owner, order_url, created_order
):

    order_date = created_order["created_at"][:10]

    response = await client.get(
        order_url,
        params={
            "start_date": order_date,
            "end_date": order_date
        },
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_filter_orders_outside_date_range(
    client, owner, order_url, created_order
):

    tomorrow = (
        datetime.now(timezone.utc).date()
        + timedelta(days=1)
    ).isoformat()

    response = await client.get(
        order_url,
        params={"start_date": tomorrow},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_invalid_date_range(
    client, owner, order_url
):

    response = await client.get(
        order_url,
        params={
            "start_date": "2026-11-25",
            "end_date": "2026-11-20"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_order_not_found(
    client, owner, order_url
):

    response = await client.get(
        f"{order_url}/{uuid4()}",
        headers=owner["headers"]
    )

    assert response.status_code == 404


async def test_cancel_order(
    client, owner, order_url, created_order
):

    response = await client.post(
        f"{order_url}/{created_order['id']}/cancel",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    order = response.json()

    assert order["status"] == "cancelled"
    assert len(order["order_items"]) == 2

    assert Decimal(
        order["total_amount"]
    ) == Decimal("750.00")


async def test_cancellation_restores_stock(
    client, owner, shop, products,
    order_url, created_order
):

    response = await client.post(
        f"{order_url}/{created_order['id']}/cancel",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    for product in products:

        stock = await get_stock(
            client, owner["headers"],
            shop["id"], product["id"]
        )

        assert stock == product["stock_quantity"]


async def test_cannot_cancel_order_twice(
    client, owner, shop, products,
    order_url, created_order
):

    url = f"{order_url}/{created_order['id']}/cancel"

    response = await client.post(
        url,
        headers=owner["headers"]
    )

    assert response.status_code == 200

    response = await client.post(
        url,
        headers=owner["headers"]
    )

    assert response.status_code == 409

    # Ensure stock was not restored twice.
    for product in products:

        stock = await get_stock(
            client, owner["headers"],
            shop["id"], product["id"]
        )

        assert stock == product["stock_quantity"]


async def test_cancel_order_with_inactive_product(
    client, owner, shop, products,
    order_url, created_order
):

    response = await client.delete(
        f"/shops/{shop['id']}/products/{products[0]['id']}",
        headers=owner["headers"]
    )

    assert response.status_code == 204

    response = await client.post(
        f"{order_url}/{created_order['id']}/cancel",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    stock = await get_stock(
        client, owner["headers"],
        shop["id"], products[0]["id"]
    )

    assert stock == 100


async def test_cancel_nonexistent_order(
    client, owner, order_url
):

    response = await client.post(
        f"{order_url}/{uuid4()}/cancel",
        headers=owner["headers"]
    )

    assert response.status_code == 404


async def test_filter_cancelled_orders(
    client, owner, order_url, created_order
):

    response = await client.post(
        f"{order_url}/{created_order['id']}/cancel",
        headers=owner["headers"]
    )

    assert response.status_code == 200

    response = await client.get(
        order_url,
        params={"status": "cancelled"},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "cancelled"


async def test_create_order_without_auth(
    client, order_url, order_data
):

    response = await client.post(
        order_url,
        json=order_data
    )

    assert response.status_code == 401


async def test_cannot_create_order_in_another_users_shop(
    client, another_user, order_url, order_data
):

    response = await client.post(
        order_url,
        json=order_data,
        headers=another_user["headers"]
    )

    assert response.status_code == 404


async def test_cannot_list_another_users_orders(
    client, another_user, order_url, created_order
):

    response = await client.get(
        order_url,
        headers=another_user["headers"]
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "method,suffix",
    [
        ("GET", ""),
        ("POST", "/cancel")
    ]
)
async def test_cross_user_order_access(
    client, another_user, order_url,
    created_order, method, suffix
):

    response = await client.request(
        method,
        f"{order_url}/{created_order['id']}{suffix}",
        headers=another_user["headers"]
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "method,suffix",
    [
        ("GET", ""),
        ("POST", "/cancel")
    ]
)
async def test_cross_shop_order_access(
    client, owner, create_shop,
    created_order, method, suffix
):

    second_shop = await create_shop(owner["headers"])

    url = (
        f"/shops/{second_shop['id']}/orders/"
        f"{created_order['id']}{suffix}"
    )

    response = await client.request(
        method,
        url,
        headers=owner["headers"]
    )

    assert response.status_code == 404


async def test_cannot_order_with_another_shops_customer(
    client, owner, create_shop,
    order_url, order_data
):

    second_shop = await create_shop(owner["headers"])

    response = await client.post(
        f"/shops/{second_shop['id']}/customers",
        json={
            "name": "Another Customer",
            "mobile": "9999999999"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 201

    order_data["customer_id"] = response.json()["id"]

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_cannot_order_another_shops_product(
    client, owner, create_shop,
    order_url, order_data
):

    second_shop = await create_shop(owner["headers"])

    response = await client.post(
        f"/shops/{second_shop['id']}/products",
        json={
            "name": "Sugar",
            "cost_price": "30.00",
            "selling_price": "40.00",
            "unit": "kg",
            "stock_quantity": 100
        },
        headers=owner["headers"]
    )

    assert response.status_code == 201

    order_data["order_items"][0]["product_id"] = (
        response.json()["id"]
    )

    response = await client.post(
        order_url,
        json=order_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422