from pydantic import BaseModel, ConfigDict, Field
from backend.app.modules.order.schema import OrderCreate, OrderResponse


class TraderCreate(BaseModel):
    id: str
    name: str = Field(min_length=1)
    phone_number: str = Field(pattern=r"^\d{10}$")
    account_number: str = Field(min_length=1)
    ifsc_code: str = Field(pattern=r"^[A-Za-z]{4}0[A-Za-z0-9]{6}$")
    business_name: str = Field(min_length=1)


class TraderResponse(BaseModel):
    id: str
    name: str
    phone_number: str
    account_number: str
    ifsc_code: str
    business_name: str

    model_config = ConfigDict(from_attributes=True)



class TraderOrderCreate(BaseModel):
    order: OrderCreate

    trader_id: str
    trader_name: str

    buying_item_ids: list[str] = Field(default_factory=list)
    transaction_ids: list[str] = Field(default_factory=list)


class TraderOrderUpdate(BaseModel):
    trader_name: str | None = None
    buying_item_ids: list[str] | None = None
    transaction_ids: list[str] | None = None


class TraderOrderResponse(BaseModel):
    order_id: str
    trader_id: str
    trader_name: str
    buying_item_ids: list[str]
    transaction_ids: list[str]

    order: OrderResponse

    model_config = ConfigDict(from_attributes=True)