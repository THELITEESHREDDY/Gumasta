from unittest.mock import AsyncMock

import pytest

from agent.state import initialize_state
from agent.schemas import ConversationOutput
from agent.nodes import (
    process_items,
    process_customer,
    prepare_order,
    submit_order
)


@pytest.fixture
def state():

    state = initialize_state("SHOP_001")

    state["catalogue"] = [
        {
            "product_id": "P001",
            "name": "Rice",
            "selling_price": "65.00",
            "unit": "kg"
        }
    ]

    return state


@pytest.fixture
def api():
    mock = AsyncMock()

    mock.get_products.return_value = [
        {
            "id": "P001",
            "name": "Rice",
            "selling_price": "65.00",
            "unit": "kg",
            "stock_quantity": 0
        }
    ]

    mock.get_customers.return_value = []

    return mock


def test_process_items(state):

    extracted = ConversationOutput(
        intent="add_items",
        items=[
            {"product_name": "Rice", "quantity": 2}
        ],
        response=""
    )

    result = process_items(state, extracted)

    assert result["requested_items"] == [
        {"product_id": "P001", "quantity": 2}
    ]


def test_unknown_product(state):

    extracted = ConversationOutput(
        intent="add_items",
        items=[
            {"product_name": "Chocolate", "quantity": 2}
        ],
        response=""
    )

    result = process_items(state, extracted)

    assert len(result["errors"]) == 1


@pytest.mark.asyncio
async def test_collect_customer_details(state, api):

    extracted = ConversationOutput(
        intent="provide_customer_details",
        customer_name="Ramesh",
        mobile="9876543211",
        response=""
    )

    result = await process_customer(
        state, extracted, api
    )

    assert result["customer"]["name"] == "Ramesh"
    assert result["customer"]["mobile"] == "9876543211"

    api.create_customer.assert_not_called()


@pytest.mark.asyncio
async def test_prepare_order(state, api):

    state["customer"] = {
        "customer_id": "C001",
        "name": "Ramesh",
        "mobile": "9876543211"
    }

    state["requested_items"] = [
        {"product_id": "P001", "quantity": 2}
    ]

    result = await prepare_order(state, api)

    assert result["status"] == "awaiting_confirmation"
    assert result["order_draft"]["total_amount"] == "130.00"
    assert result["confirmed"] is False


@pytest.mark.asyncio
async def test_reject_unconfirmed_submission(state, api):

    with pytest.raises(ValueError):
        await submit_order(state, api)

    api.create_order.assert_not_called()


@pytest.mark.asyncio
async def test_submit_order(state, api):

    state["customer"] = {
        "customer_id": "C001",
        "name": "Ramesh",
        "mobile": "9876543211"
    }

    state["requested_items"] = [
        {"product_id": "P001", "quantity": 2}
    ]

    state.update(
        await prepare_order(state, api)
    )

    state["confirmed"] = True

    api.create_order.return_value = {
        "id": "ORDER_001",
        "total_amount": "130.00"
    }

    result = await submit_order(state, api)

    assert result["status"] == "completed"
    assert result["order_id"] == "ORDER_001"

    api.create_order.assert_awaited_once()