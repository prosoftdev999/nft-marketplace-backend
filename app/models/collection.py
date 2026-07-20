from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin


class Collection(TimestampMixin, Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(140),
        unique=True,
        index=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    banner_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
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

    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
