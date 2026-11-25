import os

import httpx
import pytest
from dotenv import load_dotenv

from services.gumasta_api import GumastaAPI

load_dotenv()

BASE_URL = os.getenv(
    "GUMASTA_API_URL",
    "http://localhost:8000"
)


@pytest.mark.asyncio
async def test_backend_health():

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/health"
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_authenticated_connection():

    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": "owner@example.com",
                "password": "Test@1234"
            }
        )

    assert response.status_code == 200

    token = response.json()["access_token"]

    api = GumastaAPI(token)

    user = await api.get_current_user()

    assert user["email"] == "owner@example.com"

    shops = await api.get_shops()

    assert isinstance(shops, list)
    assert len(shops) > 0

    shop = await api.get_shop(shops[0]["id"])

    assert shop["id"] == shops[0]["id"]

    print("\nConnected successfully")
    print("Owner:", user["name"])
    print("Shop:", shop["name"])