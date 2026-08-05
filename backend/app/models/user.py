from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.inventory import Inventory, UserInventory
    from app.models.order import Order
    from app.models.wallet import Wallet


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Relationships
    wallet: Mapped[Optional["Wallet"]] = relationship(
        "Wallet",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    user_inventories: Mapped[List["UserInventory"]] = relationship(
        "UserInventory",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
    )
