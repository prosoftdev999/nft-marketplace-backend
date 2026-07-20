from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.listing import ListingCreate


def test_listing_schema_accepts_positive_price() -> None:
    listing = ListingCreate(
        nft_id=1,
        price=Decimal("1.50"),
        currency="ETH",
    )

    assert listing.price == Decimal("1.50")


def test_listing_schema_rejects_zero_price() -> None:
    with pytest.raises(ValidationError):
        ListingCreate(
            nft_id=1,
            price=Decimal("0"),
            currency="ETH",
        )
