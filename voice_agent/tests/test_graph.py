from unittest.mock import AsyncMock

import pytest

from agent.state import initialize_state
from agent.schemas import ConversationOutput
from agent.graph import (
    build_agent_graph,
    run_conversation
)


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

    mock.get_customers.return_value = [
        {
            "id": "C001",
            "name": "Ramesh",
            "mobile": "9876543211"
        }
    ]

    mock.create_order.return_value = {
        "id": "ORDER_001",
        "total_amount": "130.00"
    }

    return mock


@pytest.mark.asyncio
async def test_complete_conversation(api, monkeypatch):

    mock_extraction = AsyncMock(
        side_effect=[
            ConversationOutput(
                intent="add_items",
                items=[
                    {
                        "product_name": "Rice",
                        "quantity": 2
                    }
                ],
                response=""
            ),
            ConversationOutput(
                intent="provide_customer_details",
                mobile="9876543211",
                response=""
            ),
            ConversationOutput(
                intent="confirm_order",
                response=""
            )
        ]
    )

    monkeypatch.setattr(
        "agent.graph.extract_conversation",
        mock_extraction
    )

    graph = build_agent_graph(api)

    state = initialize_state("SHOP_001")

    # Turn 1
    state = await run_conversation(
        graph,
        state,
        "I need 2 kg rice"
    )

    print("\nAgent:", state["response"])

    assert state["status"] == "collecting_details"
    assert len(state["requested_items"]) == 1

    # Turn 2
    state = await run_conversation(
        graph,
        state,
        "9876543211"
    )

    print("\nAgent:", state["response"])

    assert state["status"] == "awaiting_confirmation"
    assert state["order_draft"]["total_amount"] == "130.00"

    api.create_order.assert_not_called()

    # Turn 3
    state = await run_conversation(
        graph,
        state,
        "Yes, confirm my order"
    )

    print("\nAgent:", state["response"])

    assert state["status"] == "completed"
    assert state["order_id"] == "ORDER_001"

    api.create_order.assert_awaited_once()

    # Prevent repeated submission
    state = await run_conversation(
        graph,
        state,
        "Confirm again"
    )

    api.create_order.assert_awaited_once()