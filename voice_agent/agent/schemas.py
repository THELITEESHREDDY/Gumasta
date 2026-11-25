from typing import Literal

from pydantic import BaseModel, Field


class ExtractedItem(BaseModel):
    product_name: str
    quantity: int = Field(gt=0)


class ConversationOutput(BaseModel):

    intent: Literal[
        "greeting",
        "add_items",
        "remove_items",
        "update_items",
        "provide_customer_details",
        "confirm_order",
        "cancel_order",
        "query_product",
        "other"
    ]

    items: list[ExtractedItem] = Field(
        default_factory=list
    )

    customer_name: str | None = None

    mobile: str | None = None

    response: str