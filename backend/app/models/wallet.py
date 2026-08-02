from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.transaction import Transaction
    from app.models.user import User


class Wallet(Base, TimestampMixin):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        default=Decimal("100.00"),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="wallet")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        back_populates="wallet",
        cascade="all, delete-orphan",
    )
