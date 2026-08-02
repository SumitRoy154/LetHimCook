from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.order import Order


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    score: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    review: Mapped[str] = mapped_column(Text, nullable=False)
    suggestions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bonus_coins: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="review")
