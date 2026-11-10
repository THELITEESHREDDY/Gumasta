from pydantic import BaseModel, ConfigDict, Field


class ShopCreate(BaseModel):
    id: str
    shop_name: str = Field(min_length=1)
    branch_address: str = Field(min_length=1)
    GST_id: str | None = None
    bank_account_number: str = Field(min_length=1)
    IFSC_code: str = Field(min_length=1)
    Payment_mobile_number: str = Field(min_length=10, max_length=10)


class ShopUpdate(BaseModel):
    shop_name: str | None = Field(default=None, min_length=1)
    branch_address: str | None = Field(default=None, min_length=1)
    GST_id: str | None = None
    bank_account_number: str | None = None
    IFSC_code: str | None = None
    Payment_mobile_number: str | None = Field(
        default=None,
        min_length=10,
        max_length=10,
    )


class ShopPublicResponse(BaseModel):
    id: str
    shop_name: str
    branch_address: str

    model_config = ConfigDict(from_attributes=True)


class ShopOwnerResponse(ShopPublicResponse):
    owner_id: str
    GST_id: str | None
    bank_account_number: str
    IFSC_code: str
    Payment_mobile_number: str