import os

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv(
    "GUMASTA_API_URL",
    "http://localhost:8000"
)


class GumastaAPI:

    def __init__(self, access_token: str):
        self.headers = {
            "Authorization": f"Bearer {access_token}"
        }

    async def request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ):
        async with httpx.AsyncClient(
            base_url=BASE_URL,
            headers=self.headers,
            timeout=15.0
        ) as client:

            response = await client.request(
                method,
                endpoint,
                **kwargs
            )

            response.raise_for_status()

            return response.json()

    async def get_current_user(self):
        return await self.request(
            "GET",
            "/auth/me"
        )

    async def get_shops(self):
        return await self.request(
            "GET",
            "/shops"
        )

    async def get_shop(self, shop_id: str):
        return await self.request(
            "GET",
            f"/shops/{shop_id}"
        )

    async def get_customers(
        self,
        shop_id: str,
        search: str
    ):
        return await self.request(
            "GET",
            f"/shops/{shop_id}/customers",
            params={"search": search}
        )


    async def create_customer(
        self,
        shop_id: str,
        name: str,
        mobile: str
    ):
        return await self.request(
            "POST",
            f"/shops/{shop_id}/customers",
            json={
                "name": name,
                "mobile": mobile
            }
        )

    async def get_products(self, shop_id: str):
        return await self.request(
            "GET",
            f"/shops/{shop_id}/products"
        )

    async def create_order(
        self,
        shop_id: str,
        customer_id: str,
        order_items: list[dict]
    ):
        return await self.request(
            "POST",
            f"/shops/{shop_id}/orders",
            json={
                "customer_id": customer_id,
                "order_items": order_items
            }
        )

    