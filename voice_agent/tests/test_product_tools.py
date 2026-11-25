from unittest.mock import AsyncMock

import pytest

from agent.tools import (
    find_product,
    get_product_catalogue
)


SHOP_ID = "SHOP_001"

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
        "stock_quantity": 20
    }
]


@pytest.fixture
def api():
    mock = AsyncMock()
    mock.get_products.return_value = PRODUCTS
    return mock


@pytest.mark.asyncio
async def test_find_existing_product(api):

    result = await find_product(
        api, SHOP_ID, "Rice"
    )

    assert result == PRODUCTS[0]


@pytest.mark.asyncio
async def test_case_insensitive_lookup(api):

    result = await find_product(
        api, SHOP_ID, "  RICE  "
    )

    assert result == PRODUCTS[0]


@pytest.mark.asyncio
async def test_product_not_found(api):

    result = await find_product(
        api, SHOP_ID, "Chocolate"
    )

    assert result is None


@pytest.mark.asyncio
async def test_zero_stock_product_is_accepted(api):

    result = await find_product(
        api, SHOP_ID, "Rice"
    )

    assert result is not None
    assert result["stock_quantity"] == 0


@pytest.mark.asyncio
async def test_product_catalogue(api):

    result = await get_product_catalogue(
        api, SHOP_ID
    )

    assert len(result) == 2

    assert result[0] == {
        "product_id": "PRODUCT_001",
        "name": "Rice",
        "selling_price": "65.00",
        "unit": "kg"
    }

    assert "stock_quantity" not in result[0]