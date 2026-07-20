import pytest
from pydantic import ValidationError

from app.schemas.collection import CollectionCreate


def test_collection_schema_accepts_valid_slug() -> None:
    collection = CollectionCreate(
        name="Genesis Collection",
        slug="genesis-collection",
        blockchain="ethereum",
    )

    assert collection.slug == "genesis-collection"


def test_collection_schema_rejects_invalid_slug() -> None:
    with pytest.raises(ValidationError):
        CollectionCreate(
            name="Genesis Collection",
            slug="Genesis Collection",
            blockchain="ethereum",
        )
