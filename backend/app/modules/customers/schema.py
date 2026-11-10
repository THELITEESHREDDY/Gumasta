from pydantic import BaseModel, Field
from typing import Optional,List


class CustomerCreate(BaseModel):
    name: str
    phone_number: str = Field(min_length=10, max_length=10, pattern=r"^\d{10}$")
    whatsApp_number: str = Field(min_length=10, max_length=10, pattern=r"^\d{10}$")


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = Field(
        default=None, min_length=10, max_length=10, pattern=r"^\d{10}$"
    )
    whatsApp_number: Optional[str] = Field(
        default=None, min_length=10, max_length=10, pattern=r"^\d{10}$"
    )


class CustomerResponse(BaseModel):
    id: str
    name: str
    phone_number: str
    whatsApp_number: str
    orders:List[CustomerOrder]
    model_config = {"from_attributes": True}