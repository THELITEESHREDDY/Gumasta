import pytest
from uuid import uuid4


@pytest.fixture
def shop_data():
    return {
        "name": "Gumasta Traders",
        "gst_id": None,
        "address": "Main Road, Hyderabad",
        "contact": "9876543210"
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
async def created_shop(client, owner, shop_data):

    response = await client.post(
        "/shops",
        json=shop_data,
        headers=owner["headers"]
    )

    assert response.status_code == 201

    return response.json()

async def test_create_shop(created_shop, owner, shop_data):

    assert created_shop["name"] == shop_data["name"]
    assert created_shop["owner_id"] == owner["user"]["id"]
    assert "id" in created_shop


async def test_list_shops(client, owner, created_shop):

    response = await client.get(
        "/shops",
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == created_shop["id"]


async def test_get_shop(client, owner, created_shop):

    response = await client.get(
        f"/shops/{created_shop['id']}",
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["id"] == created_shop["id"]


async def test_update_shop(client, owner, created_shop):

    response = await client.patch(
        f"/shops/{created_shop['id']}",
        json={"name": "Updated Shop"},
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Shop"
    assert response.json()["address"] == created_shop["address"]


async def test_nonexistent_shop(client, owner):

    response = await client.get(
        f"/shops/{uuid4()}",
        headers=owner["headers"]
    )

    assert response.status_code == 404


async def test_update_shop_with_null_name(
    client, owner, created_shop
):

    response = await client.patch(
        f"/shops/{created_shop['id']}",
        json={"name": None},
        headers=owner["headers"]
    )

    assert response.status_code == 422


async def test_create_shop_without_auth(client, shop_data):

    response = await client.post(
        "/shops",
        json=shop_data
    )

    assert response.status_code == 401


async def test_list_shops_isolation(
    client, another_user, created_shop
):

    response = await client.get(
        "/shops",
        headers=another_user["headers"]
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_cannot_access_another_users_shop(
    client, another_user, created_shop
):

    response = await client.get(
        f"/shops/{created_shop['id']}",
        headers=another_user["headers"]
    )

    assert response.status_code == 404


async def test_cannot_update_another_users_shop(
    client, owner, another_user, created_shop
):

    response = await client.patch(
        f"/shops/{created_shop['id']}",
        json={"name": "Unauthorized Update"},
        headers=another_user["headers"]
    )

    assert response.status_code == 404

    # Verify the original shop remains unchanged.
    response = await client.get(
        f"/shops/{created_shop['id']}",
        headers=owner["headers"]
    )

    assert response.status_code == 200
    assert response.json()["name"] == created_shop["name"]