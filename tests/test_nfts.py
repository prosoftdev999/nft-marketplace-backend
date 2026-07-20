import pytest
from pydantic import ValidationError

from app.schemas.nft import NFTCreate


def test_nft_schema_accepts_valid_data() -> None:
    nft = NFTCreate(
        name="Genesis NFT",
        token_id="1",
        image_url="http://localhost/image.jpg",
        collection_id=1,
    )

    assert nft.token_id == "1"
    assert nft.blockchain == "ethereum"


def test_nft_schema_rejects_invalid_collection_id() -> None:
    with pytest.raises(ValidationError):
        NFTCreate(
            name="Genesis NFT",
            token_id="1",
            image_url="http://localhost/image.jpg",
            collection_id=0,
        )
