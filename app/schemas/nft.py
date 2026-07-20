from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class NFTCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    token_id: str = Field(min_length=1, max_length=120)
    metadata_uri: str | None = None
    image_url: str = Field(min_length=1, max_length=500)
    contract_address: str | None = Field(default=None, max_length=100)
    blockchain: str = Field(default="ethereum", max_length=40)
    attributes: list[dict[str, Any]] = Field(default_factory=list)
    collection_id: int = Field(gt=0)


class NFTUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    metadata_uri: str | None = None
    image_url: str | None = Field(default=None, min_length=1, max_length=500)
    attributes: list[dict[str, Any]] | None = None


class NFTRead(BaseModel):
    id: int
    name: str
    description: str | None
    token_id: str
    metadata_uri: str | None
    image_url: str
    contract_address: str | None
    blockchain: str
    attributes: list[dict[str, Any]]
    owner_id: int
    creator_id: int
    collection_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
