from unittest.mock import AsyncMock

import pytest

from agent.tools import (
    calculate_order_total,
    place_order
)


SHOP_ID = "SHOP_001"
CUSTOMER_ID = "CUSTOMER_001"

PRODUCTS = [
    {
        "id": "PRODUCT_001",
        "name": "Rice",
        "selling_price": "65.00",
        "unit": "kg",
        "stock_quantity": 0
    },
    {
        "id": "PRODUCT_002",
        "name": "Sugar",
        "selling_price": "45.00",
        "unit": "kg",
        "stock_quantity": 10
    }
]

ITEMS = [
    {
        "product_id": "PRODUCT_001",
        "quantity": 2
    },
    {
        "product_id": "PRODUCT_002",
        "quantity": 1
    }
]


@pytest.fixture
def api():
    mock = AsyncMock()
    mock.get_products.return_value = PRODUCTS
    return mock


@pytest.mark.asyncio
async def test_calculate_order_total(api):

    result = await calculate_order_total(
        api, SHOP_ID, ITEMS
    )

    assert result["total_amount"] == "175.00"
    assert len(result["order_items"]) == 2

    assert result["order_items"][0]["subtotal"] == "130.00"


@pytest.mark.asyncio
async def test_ignore_stock_quantity(api):

    result = await calculate_order_total(
        api,
        SHOP_ID,
        [
            {
                "product_id": "PRODUCT_001",
                "quantity": 100
            }
        ]
    )

    assert result["total_amount"] == "6500.00"


@pytest.mark.asyncio
async def test_unknown_product(api):

    with pytest.raises(ValueError, match="Product not found"):

        await calculate_order_total(
            api,
            SHOP_ID,
            [
                {
                    "product_id": "UNKNOWN",
                    "quantity": 2
                }
            ]
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("quantity", [0, -1, 1.5, True])
async def test_invalid_quantity(api, quantity):

    with pytest.raises(ValueError, match="Invalid quantity"):

        await calculate_order_total(
            api,
            SHOP_ID,
            [
                {
                    "product_id": "PRODUCT_001",
                    "quantity": quantity
                }
            ]
        )


@pytest.mark.asyncio
async def test_duplicate_products(api):

    result = await calculate_order_total(
        api,
        SHOP_ID,
        [
            {
                "product_id": "PRODUCT_001",
                "quantity": 2
            },
            {
                "product_id": "PRODUCT_001",
                "quantity": 3
            }
        ]
    )

    assert len(result["order_items"]) == 1
    assert result["order_items"][0]["quantity"] == 5
    assert result["total_amount"] == "325.00"


@pytest.mark.asyncio
async def test_empty_order(api):

    with pytest.raises(ValueError):
        await calculate_order_total(api, SHOP_ID, [])


@pytest.mark.asyncio
async def test_place_confirmed_order(api):

    api.create_order.return_value = {
        "id": "ORDER_001",
        "total_amount": "175.00",
        "status": "completed"
    }

    calculated = await calculate_order_total(
        api, SHOP_ID, ITEMS
    )

    result = await place_order(
        api,
        SHOP_ID,
        CUSTOMER_ID,
        calculated["order_items"],
        confirmed=True
    )

    assert result["id"] == "ORDER_001"

    api.create_order.assert_awaited_once_with(
        shop_id=SHOP_ID,
        customer_id=CUSTOMER_ID,
        order_items=[
            {
                "product_id": "PRODUCT_001",
                "quantity": 2,
                "unit_price": "65.00"
            },
            {
                "product_id": "PRODUCT_002",
                "quantity": 1,
                "unit_price": "45.00"
            }
        ]
    )


@pytest.mark.asyncio
async def test_reject_unconfirmed_order(api):

    with pytest.raises(ValueError):

        await place_order(
            api,
            SHOP_ID,
            CUSTOMER_ID,
            ITEMS,
            confirmed=False
        )

    api.create_order.assert_not_called()