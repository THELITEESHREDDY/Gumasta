from unittest.mock import AsyncMock

import pytest

from agent.tools import (
    find_customer,
    get_or_create_customer
)


SHOP_ID = "SHOP_001"

CUSTOMER = {
    "id": "CUSTOMER_001",
    "name": "Ramesh Kumar",
    "mobile": "9876543211"
}


@pytest.fixture
def api():
    return AsyncMock()


@pytest.mark.asyncio
async def test_find_existing_customer(api):

    api.get_customers.return_value = [CUSTOMER]

    result = await find_customer(
        api,
        SHOP_ID,
        "9876543211"
    )

    assert result == CUSTOMER


@pytest.mark.asyncio
async def test_customer_not_found(api):

    api.get_customers.return_value = []

    result = await find_customer(
        api,
        SHOP_ID,
        "9876543211"
    )

    assert result is None


@pytest.mark.asyncio
async def test_reuse_existing_customer(api):

    api.get_customers.return_value = [CUSTOMER]

    result = await get_or_create_customer(
        api,
        SHOP_ID,
        "9876543211"
    )

    assert result["status"] == "existing"
    assert result["customer"] == CUSTOMER

    api.create_customer.assert_not_called()


@pytest.mark.asyncio
async def test_new_customer_requires_name(api):

    api.get_customers.return_value = []

    result = await get_or_create_customer(
        api,
        SHOP_ID,
        "9876543211"
    )

    assert result["status"] == "name_required"
    assert result["customer"] is None

    api.create_customer.assert_not_called()


@pytest.mark.asyncio
async def test_create_new_customer(api):

    api.get_customers.return_value = []
    api.create_customer.return_value = CUSTOMER

    result = await get_or_create_customer(
        api,
        SHOP_ID,
        "9876543211",
        "Ramesh Kumar"
    )

    assert result["status"] == "created"
    assert result["customer"] == CUSTOMER

    api.create_customer.assert_awaited_once_with(
        SHOP_ID,
        name="Ramesh Kumar",
        mobile="9876543211"
    )


@pytest.mark.asyncio
async def test_invalid_mobile(api):

    with pytest.raises(ValueError):
        await get_or_create_customer(
            api,
            SHOP_ID,
            "123"
        )

    api.get_customers.assert_not_called()
    api.create_customer.assert_not_called()