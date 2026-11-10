from pydantic import BaseModel, Field, ConfigDict


class ItemCreate(BaseModel):
    id: str
    name: str = Field(min_length=1)
    selling_price: float = Field(ge=0)
    cost_price: float = Field(ge=0)
    quantity: float = Field(ge=0)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    selling_price: float | None = Field(default=None, ge=0)
    cost_price: float | None = Field(default=None, ge=0)
    quantity: float | None = Field(default=None, ge=0)


class ItemResponse(BaseModel):
    id: str
    name: str
    selling_price: float
    cost_price: float
    quantity: float

    model_config = ConfigDict(from_attributes=True)