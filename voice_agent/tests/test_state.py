import pytest

from pydantic import ValidationError

from agent.state import initialize_state
from agent.schemas import ConversationOutput


def test_initialize_state():

    state = initialize_state("SHOP_001")

    assert state["shop_id"] == "SHOP_001"
    assert state["status"] == "collecting_details"
    assert state["confirmed"] is False
    assert state["requested_items"] == []
    assert state["order_draft"] is None
    assert state["customer"]["customer_id"] is None


def test_independent_conversation_states():

    state1 = initialize_state("SHOP_001")
    state2 = initialize_state("SHOP_001")

    state1["customer"]["name"] = "Ramesh"

    assert state2["customer"]["name"] is None


def test_extract_order_items():

    result = ConversationOutput(
        intent="add_items",
        items=[
            {
                "product_name": "Rice",
                "quantity": 2
            }
        ],
        response="Sure, 2 kg rice."
    )

    assert result.items[0].product_name == "Rice"
    assert result.items[0].quantity == 2


def test_invalid_quantity():

    with pytest.raises(ValidationError):

        ConversationOutput(
            intent="add_items",
            items=[
                {
                    "product_name": "Rice",
                    "quantity": -1
                }
            ],
            response=""
        )


def test_confirmation_intent():

    result = ConversationOutput(
        intent="confirm_order",
        response="Confirming your order."
    )

    assert result.intent == "confirm_order"
    assert result.items == []


def test_invalid_intent():

    with pytest.raises(ValidationError):

        ConversationOutput(
            intent="unknown",
            response=""
        )