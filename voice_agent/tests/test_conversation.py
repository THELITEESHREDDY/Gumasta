import pytest

from langchain_core.messages import HumanMessage

from agent.state import initialize_state
from agent.nodes import extract_conversation


@pytest.fixture
def state():

    state = initialize_state("SHOP_001")

    state["catalogue"] = [
        {
            "product_id": "PRODUCT_001",
            "name": "Rice",
            "selling_price": "65.00",
            "unit": "kg"
        },
        {
            "product_id": "PRODUCT_002",
            "name": "Sugar",
            "selling_price": "45.00",
            "unit": "kg"
        }
    ]

    return state


@pytest.mark.asyncio
async def test_extract_products(state):

    state["messages"] = [
        HumanMessage(
            content="I need 2 kg rice and 1 kg sugar"
        )
    ]

    result = await extract_conversation(state)

    print(result.model_dump_json(indent=2))

    assert result.intent == "add_items"

    items = {
        item.product_name.lower(): item.quantity
        for item in result.items
    }

    assert items["rice"] == 2
    assert items["sugar"] == 1


@pytest.mark.asyncio
async def test_extract_customer_details(state):

    state["messages"] = [
        HumanMessage(
            content="My name is Ramesh and my number is 9876543211"
        )
    ]

    result = await extract_conversation(state)

    print(result.model_dump_json(indent=2))

    assert result.customer_name == "Ramesh"
    assert result.mobile == "9876543211"


@pytest.mark.asyncio
async def test_confirm_order(state):

    state["status"] = "awaiting_confirmation"

    state["messages"] = [
        HumanMessage(
            content="Yes, confirm my order"
        )
    ]

    result = await extract_conversation(state)

    assert result.intent == "confirm_order"