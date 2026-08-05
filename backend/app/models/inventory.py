from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Inventory(Base, TimestampMixin):
    """Global items catalog definition."""
    __tablename__ = "inventories"

    ingredient_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ingredient_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    purchase_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=Decimal("0.00"),
        nullable=False,
    )

    # Relationships
    user_inventories: Mapped[List["UserInventory"]] = relationship(
        "UserInventory", back_populates="item", cascade="all, delete-orphan"
    )


class UserInventory(Base, TimestampMixin):
    """User-specific inventory stock tracking."""
    __tablename__ = "user_inventories"

    __table_args__ = (
        UniqueConstraint("user_id", "ingredient_id", name="uq_user_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("inventories.ingredient_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_inventories")
    item: Mapped["Inventory"] = relationship("Inventory", back_populates="user_inventories")
