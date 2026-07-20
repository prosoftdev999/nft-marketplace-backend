from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class UserCreate(BaseModel):
    email: EmailStr

    username: str = Field(
        min_length=3,
        max_length=50,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    wallet_address: str | None = Field(
        default=None,
        max_length=100,
    )


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    wallet_address: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
