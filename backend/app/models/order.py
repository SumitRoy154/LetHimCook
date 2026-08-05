from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.dish_pipeline import DishIngredient, DishRecipe
    from app.models.review import Review
    from app.models.shopping import ShoppingHistory
    from app.models.user import User


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    dish_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    reward_received: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    dish_ingredient: Mapped[Optional["DishIngredient"]] = relationship(
        "DishIngredient",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )
    dish_recipe: Mapped[Optional["DishRecipe"]] = relationship(
        "DishRecipe",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )
    shopping_items: Mapped[List["ShoppingHistory"]] = relationship(
        "ShoppingHistory",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    review: Mapped[Optional["Review"]] = relationship(
        "Review",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )
