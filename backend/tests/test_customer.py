import pytest
from uuid import uuid4


@pytest.fixture
def customer_data():
    return {
        "name": "Ravi Kumar",
        "mobile": "9876543210",
        "alternate_mobile": "9123456780",
        "address": "Main Road, Hyderabad"
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
def customer_url(shop):
    return f"/shops/{shop['id']}/customers"


@pytest.fixture
async def created_customer(
    client, owner, customer_url, customer_data
):

    response = await client.post(
        customer_url,
        json=customer_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201

    return response.json()


async def test_create_customer(created_customer, shop):

    assert created_customer["name"] == "Ravi Kumar"
    assert created_customer["mobile"] == "9876543210"
    assert created_customer["shop_id"] == shop["id"]
    assert created_customer["alternate_mobile"] == "9123456780"


async def test_create_customer_without_optional_fields(
    client, owner, customer_url
):

    response = await client.post(
        customer_url,
        json={
            "name": "Ramesh",
            "mobile": "9999999999"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 201
    assert response.json()["address"] is None
    assert response.json()["alternate_mobile"] is None


async def test_list_customers(
    client, owner, customer_url, created_customer
):

    response = await client.get(
        customer_url,
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == created_customer["id"]


async def test_get_customer(
    client, owner, customer_url, created_customer
):

    response = await client.get(
        f"{customer_url}/{created_customer['id']}",
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["id"] == created_customer["id"]


async def test_update_customer(
    client, owner, customer_url, created_customer
):

    response = await client.patch(
        f"{customer_url}/{created_customer['id']}",
        json={
            "name": "Ravi Sharma",
            "mobile": "9999999999",
            "address": "New Address"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Ravi Sharma"
    assert data["mobile"] == "9999999999"
    assert data["address"] == "New Address"
    assert data["alternate_mobile"] == "9123456780"


async def test_clear_optional_fields(
    client, owner, customer_url, created_customer
):

    response = await client.patch(
        f"{customer_url}/{created_customer['id']}",
        json={
            "address": None,
            "alternate_mobile": None
        },
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["address"] is None
    assert response.json()["alternate_mobile"] is None


async def test_customer_not_found(
    client, owner, customer_url
):

    response = await client.get(
        f"{customer_url}/{uuid4()}",
        headers=owner["headers"]
    )

    assert response.status_code == 404


async def test_duplicate_mobile_same_shop(
    client, owner, customer_url,
    customer_data, created_customer
):

    response = await client.post(
        customer_url,
        json=customer_data,
        headers=owner["headers"]
    )

    assert response.status_code == 409


async def test_same_mobile_different_shops(
    client, owner, create_shop,
    customer_data, created_customer
):

    second_shop = await create_shop(owner["headers"])

    response = await client.post(
        f"/shops/{second_shop['id']}/customers",
        json=customer_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201
    assert response.json()["id"] != created_customer["id"]
    assert response.json()["mobile"] == created_customer["mobile"]


async def test_update_to_duplicate_mobile(
    client, owner, customer_url, created_customer
):

    response = await client.post(
        customer_url,
        json={
            "name": "Suresh",
            "mobile": "9999999999"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 201

    second_customer = response.json()

    url = f"{customer_url}/{second_customer['id']}"

    response = await client.patch(
        url,
        json={"mobile": created_customer["mobile"]},
        headers=owner["headers"]
    )

    assert response.status_code == 409

    # Verify the original mobile remains unchanged.
    response = await client.get(
        url,
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["mobile"] == "9999999999"


async def test_update_with_same_mobile(
    client, owner, customer_url, created_customer
):

    response = await client.patch(
        f"{customer_url}/{created_customer['id']}",
        json={"mobile": created_customer["mobile"]},
        headers=owner["headers"]
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "search",
    [
        "Ravi",
        "ravi",
        "Kumar",
        "98765",
        "91234",
        "  Ravi  "
    ]
)
async def test_search_customers(
    client, owner, customer_url,
    created_customer, search
):

    response = await client.post(
        customer_url,
        json={
            "name": "Suresh",
            "mobile": "9999999999"
        },
        headers=owner["headers"]
    )

    assert response.status_code == 201

    response = await client.get(
        customer_url,
        params={"search": search},
        headers=owner["headers"]
    )

    assert response.status_code == 200

    customers = response.json()

    assert len(customers) == 1
    assert customers[0]["id"] == created_customer["id"]


async def test_search_no_matching_customers(
    client, owner, customer_url, created_customer
):

    response = await client.get(
        customer_url,
        params={"search": "Unknown Customer"},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_search_empty_string(
    client, owner, customer_url, created_customer
):

    response = await client.get(
        customer_url,
        params={"search": ""},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_search_wildcard_is_escaped(
    client, owner, customer_url, created_customer
):

    response = await client.get(
        customer_url,
        params={"search": "%"},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", ""),
        ("name", None),
        ("mobile", "123"),
        ("mobile", "abcdefghij"),
        ("mobile", None),
        ("alternate_mobile", "123"),
        ("address", "a" * 501)
    ]
)
async def test_invalid_customer_creation(
    client, owner, customer_url,
    customer_data, field, value
):

    customer_data[field] = value

    response = await client.post(
        customer_url,
        json=customer_data,
        headers=owner["headers"]
    )

    assert response.status_code == 422


@pytest.mark.parametrize("field", ["name", "mobile"])
async def test_update_required_field_to_null(
    client, owner, customer_url,
    created_customer, field
):

    response = await client.patch(
        f"{customer_url}/{created_customer['id']}",
        json={field: None},
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_create_customer_without_auth(
    client, customer_url, customer_data
):

    response = await client.post(
        customer_url,
        json=customer_data
    )

    assert response.status_code == 401


async def test_cannot_create_customer_in_another_users_shop(
    client, another_user, customer_url, customer_data
):

    response = await client.post(
        customer_url,
        json=customer_data,
        headers=another_user["headers"]
    )

    assert response.status_code == 404


async def test_cannot_list_another_users_customers(
    client, another_user, customer_url, created_customer
):

    response = await client.get(
        customer_url,
        headers=another_user["headers"]
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "method,payload",
    [
        ("GET", None),
        ("PATCH", {"name": "Unauthorized"})
    ]
)
async def test_cross_user_customer_access(
    client, another_user, customer_url,
    created_customer, method, payload
):

    response = await client.request(
        method,
        f"{customer_url}/{created_customer['id']}",
        json=payload,
        headers=another_user["headers"]
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "method,payload",
    [
        ("GET", None),
        ("PATCH", {"name": "Unauthorized"})
    ]
)
async def test_cross_shop_customer_access(
    client, owner, create_shop,
    created_customer, method, payload
):

    second_shop = await create_shop(owner["headers"])

    url = (
        f"/shops/{second_shop['id']}/customers/"
        f"{created_customer['id']}"
    )

    response = await client.request(
        method,
        url,
        json=payload,
        headers=owner["headers"]
    )

    assert response.status_code == 404


async def test_customer_search_shop_isolation(
    client, owner, create_shop, created_customer
):

    second_shop = await create_shop(owner["headers"])

    response = await client.get(
        f"/shops/{second_shop['id']}/customers",
        params={"search": created_customer["name"]},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json() == []