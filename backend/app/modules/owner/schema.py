from pydantic import BaseModel, EmailStr, Field, ConfigDict


class OwnerRegister(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    phone_number: str = Field(pattern=r"^[0-9]{10}$")


class OwnerLogin(BaseModel):
    email: EmailStr
    password: str


class OwnerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    email: EmailStr | None = None
    phone_number: str | None = Field(
        default=None, pattern=r"^[0-9]{10}$"
    )


class OwnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: EmailStr
    is_verified: bool
    phone_number: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"