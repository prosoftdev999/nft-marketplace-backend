from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.listing import ListingStatus


class ListingCreate(BaseModel):
    nft_id: int = Field(gt=0)
    price: Decimal = Field(gt=0)
    currency: str = Field(default="ETH", min_length=1, max_length=20)


class ListingRead(BaseModel):
    id: int
    nft_id: int
    seller_id: int
    buyer_id: int | None
    price: Decimal
    currency: str
    status: ListingStatus
    listed_at: datetime
    sold_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
