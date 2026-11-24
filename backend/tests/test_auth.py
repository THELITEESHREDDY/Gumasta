import pytest


@pytest.fixture
def user_data():
    return {
        "name": "Test User",
        "email": "test@example.com",
        "mobile": "9876543210",
        "password": "TestPassword123"
    }


async def test_register_user(client, user_data):

    response = await client.post(
        "/auth/register",
        json=user_data
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == user_data["email"]
    assert data["name"] == user_data["name"]
    assert "id" in data
    assert "password_hash" not in data
    assert "password" not in data


async def test_duplicate_registration(client, user_data):

    await client.post("/auth/register", json=user_data)

    response = await client.post(
        "/auth/register",
        json=user_data
    )

    assert response.status_code == 409


async def test_invalid_registration(client, user_data):

    user_data["email"] = "invalid-email"

    response = await client.post(
        "/auth/register",
        json=user_data
    )

    assert response.status_code == 422


async def test_login_success(client, user_data):

    await client.post("/auth/register", json=user_data)

    response = await client.post(
        "/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


async def test_login_wrong_password(client, user_data):

    await client.post("/auth/register", json=user_data)

    response = await client.post(
        "/auth/login",
        data={
            "username": user_data["email"],
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


async def test_login_nonexistent_user(client):

    response = await client.post(
        "/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 401


async def test_profile_without_token(client):

    response = await client.get("/auth/me")

    assert response.status_code == 401


async def test_profile_invalid_token(client):

    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401


async def test_profile_authenticated(client, user_data):

    await client.post("/auth/register", json=user_data)

    login_response = await client.post(
        "/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )

    token = login_response.json()["access_token"]

    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]
    assert "password_hash" not in response.json()