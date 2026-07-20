from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class ListingStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    CANCELLED = "cancelled"


class Listing(TimestampMixin, Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True)

    nft_id: Mapped[int] = mapped_column(
        ForeignKey("nfts.id", ondelete="CASCADE"),
        nullable=False,
    )

    seller_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    buyer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(30, 8),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(20),
        default="ETH",
        nullable=False,
    )

    status: Mapped[ListingStatus] = mapped_column(
        SQLEnum(ListingStatus, name="listing_status"),
        default=ListingStatus.ACTIVE,
        nullable=False,
    )

    listed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    sold_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
