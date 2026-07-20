from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(
        min_length=1,
        max_length=140,
        pattern=r"^[a-z0-9-]+$",
    )
    description: str | None = None
    image_url: str | None = None
    banner_url: str | None = None
    contract_address: str | None = None
    blockchain: str = Field(default="ethereum", max_length=40)


class CollectionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    image_url: str | None = None
    banner_url: str | None = None
    contract_address: str | None = None
    blockchain: str | None = Field(default=None, max_length=40)


class CollectionRead(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    image_url: str | None
    banner_url: str | None
    contract_address: str | None
    blockchain: str
    creator_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
