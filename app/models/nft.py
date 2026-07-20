from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKey, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin


class NFT(TimestampMixin, Base):
    __tablename__ = "nfts"

    __table_args__ = (
        UniqueConstraint(
            "contract_address",
            "token_id",
            name="uq_nft_contract_token",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    token_id: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    metadata_uri: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    contract_address: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    blockchain: Mapped[str] = mapped_column(
        String(40),
        default="ethereum",
        nullable=False,
    )

    attributes: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    collection_id: Mapped[int] = mapped_column(
        ForeignKey(
            "collections.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="nft",
        cascade="all, delete-orphan",
    )
