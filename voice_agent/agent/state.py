from typing import TypedDict, Literal

from langchain_core.messages import BaseMessage
from typing import TypedDict, Literal, NotRequired
from agent.schemas import ConversationOutput


class CustomerState(TypedDict):
    customer_id: str | None
    name: str | None
    mobile: str | None


class RequestedItem(TypedDict):
    product_id: str
    quantity: int


class OrderItem(TypedDict):
    product_id: str
    product_name: str
    quantity: int
    unit: str
    unit_price: str
    subtotal: str


class OrderDraft(TypedDict):
    order_items: list[OrderItem]
    total_amount: str


class AgentState(TypedDict):
    shop_id: str

    messages: list[BaseMessage]

    catalogue: list[dict]

    customer: CustomerState

    requested_items: list[RequestedItem]

    order_draft: OrderDraft | None

    status: Literal[
        "collecting_details",
        "awaiting_confirmation",
        "placing_order",
        "completed",
        "cancelled",
        "failed"
    ]

    confirmed: bool

    order_id: str | None

    response: str

    errors: list[str]

    extracted: NotRequired[ConversationOutput]


def initialize_state(shop_id: str) -> AgentState:

    return {
        "shop_id": shop_id,

        "messages": [],

        "catalogue": [],

        "customer": {
            "customer_id": None,
            "name": None,
            "mobile": None
        },

        "requested_items": [],

        "order_draft": None,

        "status": "collecting_details",

        "confirmed": False,

        "order_id": None,

        "response": "",

        "errors": []
    }