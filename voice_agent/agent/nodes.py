import json

from langchain_core.messages import SystemMessage

from services.llm import llm_service
from agent.state import AgentState
from agent.schemas import ConversationOutput
from agent.prompts import conversation_prompt

import re

from services.gumasta_api import GumastaAPI

from agent.tools import (
    get_product_catalogue,
    find_customer,
    get_or_create_customer,
    calculate_order_total,
    place_order
)

async def extract_conversation(
    state: AgentState
) -> ConversationOutput:

    context = {
        "catalogue": state["catalogue"],
        "customer": state["customer"],
        "requested_items": state["requested_items"],
        "order_draft": state["order_draft"],
        "status": state["status"]
    }

    messages = [
        SystemMessage(
            content=(
                conversation_prompt
                + "\nCurrent conversation state:\n"
                + json.dumps(context)
            )
        ),
        *state["messages"]
    ]

    structured_llm = llm_service.with_structured_output(
        ConversationOutput
    )

    return await structured_llm.ainvoke(messages)


async def load_catalogue(
    state: AgentState,
    api: GumastaAPI
):
    catalogue = await get_product_catalogue(
        api,
        state["shop_id"]
    )

    return {
        "catalogue": catalogue
    }


def process_items(
    state: AgentState,
    extracted: ConversationOutput
):
    catalogue = state["catalogue"]

    requested = {
        item["product_id"]: item["quantity"]
        for item in state["requested_items"]
    }

    if extracted.intent not in {
        "add_items",
        "remove_items",
        "update_items"
    }:
        return {}

    errors = []

    for item in extracted.items:

        matches = [
            product for product in catalogue
            if product["name"].strip().casefold()
            == item.product_name.strip().casefold()
        ]

        if len(matches) != 1:
            errors.append(
                f"Unknown or ambiguous product: {item.product_name}"
            )
            continue

        product_id = matches[0]["product_id"]

        if extracted.intent == "add_items":

            requested[product_id] = (
                requested.get(product_id, 0)
                + item.quantity
            )

        elif extracted.intent == "update_items":

            requested[product_id] = item.quantity

        elif extracted.intent == "remove_items":

            requested.pop(product_id, None)

    if errors:
        return {
            "errors": errors,
            "confirmed": False,
            "order_draft": None,
            "status": "collecting_details"
        }

    return {
        "requested_items": [
            {
                "product_id": product_id,
                "quantity": quantity
            }
            for product_id, quantity in requested.items()
        ],
        "order_draft": None,
        "confirmed": False,
        "status": "collecting_details"
    }

async def process_customer(
    state: AgentState,
    extracted: ConversationOutput,
    api: GumastaAPI
):
    customer = dict(state["customer"])

    if extracted.mobile:
        mobile = extracted.mobile.strip()

        if not re.fullmatch(r"\+?[0-9]{10,15}", mobile):
            return {
                "errors": ["Invalid mobile number"],
                "confirmed": False,
                "order_draft": None,
                "status": "collecting_details"
            }

        if mobile != customer["mobile"]:
            customer = {
                "customer_id": None,
                "name": None,
                "mobile": mobile
            }

    if extracted.customer_name:
        customer["name"] = extracted.customer_name.strip()

    if customer["mobile"] and not customer["customer_id"]:

        existing = await find_customer(
            api,
            state["shop_id"],
            customer["mobile"]
        )

        if existing:
            customer = {
                "customer_id": existing["id"],
                "name": existing["name"],
                "mobile": existing["mobile"]
            }

    if customer != state["customer"]:
        return {
            "customer": customer,
            "confirmed": False,
            "order_draft": None,
            "status": "collecting_details"
        }

    return {"customer": customer}


async def prepare_order(
    state: AgentState,
    api: GumastaAPI
):
    customer = state["customer"]
    extracted = state.get("extracted")

    # Handle validation errors
    if state["errors"]:
        return {
            "response": " ".join(state["errors"])
        }

    # Answer product queries without modifying the order
    if extracted and extracted.intent == "query_product":
        return {
            "response": extracted.response
        }

    # Handle empty cart
    if not state["requested_items"]:
        return {
            "response": (
                extracted.response
                if extracted and extracted.response
                else "What would you like to order?"
            )
        }

    # Collect customer mobile number
    if not customer["mobile"]:
        return {
            "response": "May I know your mobile number?"
        }

    # Collect name for new customers
    if not customer["customer_id"] and not customer["name"]:
        return {
            "response": "May I know your name?"
        }

    # Calculate order total
    draft = await calculate_order_total(
        api,
        state["shop_id"],
        state["requested_items"]
    )

    # Generate order summary
    lines = [
        f'{item["quantity"]} {item["unit"]} '
        f'{item["product_name"]} - Rs. {item["subtotal"]}'
        for item in draft["order_items"]
    ]

    summary = "\n".join(lines)

    response = (
        f'{customer["name"]}, your order is:\n'
        f'{summary}\n'
        f'Total: Rs. {draft["total_amount"]}.\n'
        "Would you like to confirm this order?"
    )

    return {
        "order_draft": draft,
        "status": "awaiting_confirmation",
        "confirmed": False,
        "response": response
    }


async def submit_order(
    state: AgentState,
    api: GumastaAPI
):
    if (
        not state["confirmed"]
        or state["status"] != "awaiting_confirmation"
        or not state["order_draft"]
        or state["order_id"]
        or state["errors"]
    ):
        raise ValueError("Order is not ready for submission")

    customer = dict(state["customer"])

    if not customer["customer_id"]:

        result = await get_or_create_customer(
            api,
            state["shop_id"],
            customer["mobile"],
            customer["name"]
        )

        if not result["customer"]:
            raise ValueError("Customer details are incomplete")

        customer["customer_id"] = result["customer"]["id"]

    order = await place_order(
        api=api,
        shop_id=state["shop_id"],
        customer_id=customer["customer_id"],
        order_items=state["order_draft"]["order_items"],
        confirmed=True
    )

    return {
        "customer": customer,
        "order_id": order["id"],
        "status": "completed",
        "confirmed": False,
        "response": (
            "Your order has been placed successfully. "
            f'Total amount is Rs. {order["total_amount"]}. '
            "Thank you!"
        )
    }