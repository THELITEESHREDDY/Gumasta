import pytest
from uuid import uuid4
from decimal import Decimal


@pytest.fixture
def product_data():
    return {
        "name": "Rice",
        "cost_price": "45.00",
        "selling_price": "55.00",
        "unit": "kg",
        "stock_quantity": 100
    }


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
                "address": "Main Road, Hyderabad",
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
def product_url(shop):
    return f"/shops/{shop['id']}/products"


@pytest.fixture
async def created_product(
    client, owner, product_url, product_data
):

    response = await client.post(
        product_url,
        json=product_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201

    return response.json()


async def test_create_product(created_product, shop):

    assert created_product["name"] == "Rice"
    assert created_product["shop_id"] == shop["id"]
    assert created_product["stock_quantity"] == 100
    assert created_product["is_active"] is True

    assert Decimal(created_product["cost_price"]) == Decimal("45.00")
    assert Decimal(created_product["selling_price"]) == Decimal("55.00")


async def test_list_products(
    client, owner, product_url, created_product
):

    response = await client.get(
        product_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == created_product["id"]


async def test_get_product(
    client, owner, product_url, created_product
):

    response = await client.get(
        f"{product_url}/{created_product['id']}",
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["id"] == created_product["id"]


async def test_update_product(
    client, owner, product_url, created_product
):

    response = await client.patch(
        f"{product_url}/{created_product['id']}",
        json={
            "name": "Premium Rice",
            "selling_price": "65.00"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Premium Rice"
    assert Decimal(data["selling_price"]) == Decimal("65.00")
    assert data["stock_quantity"] == 100


async def test_nonexistent_product(
    client, owner, product_url
):

    response = await client.get(
        f"{product_url}/{uuid4()}",
        headers=owner["headers"]
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", ""),
        ("cost_price", -10),
        ("selling_price", -10),
        ("stock_quantity", -1),
        ("unit", "")
    ]
)
async def test_invalid_product_creation(
    client, owner, product_url, product_data,
    field, value
):

    product_data[field] = value

    response = await client.post(
        product_url,
        json=product_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_update_product_with_null_name(
    client, owner, product_url, created_product
):

    response = await client.patch(
        f"{product_url}/{created_product['id']}",
        json={"name": None},
        headers=owner["headers"]
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "quantity,expected_stock",
    [
        (50, 150),
        (-20, 80),
        (-100, 0)
    ]
)
async def test_adjust_stock(
    client, owner, product_url, created_product,
    quantity, expected_stock
):

    response = await client.patch(
        f"{product_url}/{created_product['id']}/stock",
        json={"quantity": quantity},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == expected_stock


async def test_insufficient_stock(
    client, owner, product_url, created_product
):

    url = f"{product_url}/{created_product['id']}"

    response = await client.patch(
        f"{url}/stock",
        json={"quantity": -101},
        headers=owner["headers"]
    )

    assert response.status_code == 409

    # Verify stock remains unchanged.
    response = await client.get(
        url,
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["stock_quantity"] == 100


async def test_zero_stock_adjustment(
    client, owner, product_url, created_product
):

    response = await client.patch(
        f"{product_url}/{created_product['id']}/stock",
        json={"quantity": 0},
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_cumulative_stock_adjustments(
    client, owner, product_url, created_product
):

    url = f"{product_url}/{created_product['id']}/stock"

    for quantity, expected in [(50, 150), (-30, 120), (-20, 100)]:

        response = await client.patch(
            url,
            json={"quantity": quantity},
            headers=owner["headers"]
        )

        assert response.status_code == 200
        assert response.json()["stock_quantity"] == expected



async def test_deactivate_product(
    client, owner, product_url, created_product
):

    url = f"{product_url}/{created_product['id']}"

    response = await client.delete(
        url,
        headers=owner["headers"]
    )

    assert response.status_code == 204

    response = await client.get(
        url,
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


async def test_inactive_product_listing(
    client, owner, product_url, created_product
):

    await client.delete(
        f"{product_url}/{created_product['id']}",
        headers=owner["headers"]
    )

    response = await client.get(
        product_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json() == []

    response = await client.get(
        product_url,
        params={"include_inactive": True},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["is_active"] is False


async def test_cannot_adjust_inactive_product(
    client, owner, product_url, created_product
):

    url = f"{product_url}/{created_product['id']}"

    await client.delete(
        url,
        headers=owner["headers"]
    )

    response = await client.patch(
        f"{url}/stock",
        json={"quantity": 10},
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_cannot_update_inactive_product(
    client, owner, product_url, created_product
):

    url = f"{product_url}/{created_product['id']}"

    await client.delete(
        url,
        headers=owner["headers"]
    )

    response = await client.patch(
        url,
        json={"name": "Updated Rice"},
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_deactivation_is_idempotent(
    client, owner, product_url, created_product
):

    url = f"{product_url}/{created_product['id']}"

    for _ in range(2):

        response = await client.delete(
            url,
            headers=owner["headers"]
        )

        assert response.status_code == 204


async def test_create_product_without_auth(
    client, product_url, product_data
):

    response = await client.post(
        product_url,
        json=product_data
    )

    assert response.status_code == 401


async def test_cannot_list_another_users_products(
    client, another_user, product_url, created_product
):

    response = await client.get(
        product_url,
        headers=another_user["headers"]
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "method,suffix,payload",
    [
        ("GET", "", None),
        ("PATCH", "", {"name": "Unauthorized"}),
        ("PATCH", "/stock", {"quantity": -10}),
        ("DELETE", "", None)
    ]
)
async def test_cross_user_product_access(
    client, another_user, product_url, created_product,
    method, suffix, payload
):

    response = await client.request(
        method,
        f"{product_url}/{created_product['id']}{suffix}",
        json=payload,
        headers=another_user["headers"]
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "method,suffix,payload",
    [
        ("GET", "", None),
        ("PATCH", "", {"name": "Unauthorized"}),
        ("PATCH", "/stock", {"quantity": -10}),
        ("DELETE", "", None)
    ]
)
async def test_cross_shop_product_access(
    client, owner, create_shop, created_product,
    method, suffix, payload
):

    second_shop = await create_shop(owner["headers"])

    url = (
        f"/shops/{second_shop['id']}/products/"
        f"{created_product['id']}{suffix}"
    )

    response = await client.request(
        method,
        url,
        json=payload,
        headers=owner["headers"]
    )

    assert response.status_code == 404