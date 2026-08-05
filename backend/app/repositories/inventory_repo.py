from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory, UserInventory
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[Inventory]):
    def __init__(self, db: Session):
        super().__init__(Inventory, db)

    def get_by_name(self, ingredient_name: str) -> Optional[Inventory]:
        name_clean = ingredient_name.strip().lower()
        stmt = select(Inventory).where(Inventory.ingredient_name.ilike(name_clean))
        return self.db.scalars(stmt).first()


class UserInventoryRepository(BaseRepository[UserInventory]):
    def __init__(self, db: Session):
        super().__init__(UserInventory, db)

    def get_by_user_id(self, user_id: int) -> List[UserInventory]:
        stmt = (
            select(UserInventory)
            .join(UserInventory.item)
            .where(UserInventory.user_id == user_id)
        )
        return list(self.db.scalars(stmt).all())

    def get_user_item(self, user_id: int, ingredient_id: int) -> Optional[UserInventory]:
        stmt = select(UserInventory).where(
            UserInventory.user_id == user_id,
            UserInventory.ingredient_id == ingredient_id,
        )
        return self.db.scalars(stmt).first()

    def get_user_ingredient_by_name(self, user_id: int, ingredient_name: str) -> Optional[UserInventory]:
        name_clean = ingredient_name.strip().lower()
        stmt = (
            select(UserInventory)
            .join(UserInventory.item)
            .where(
                UserInventory.user_id == user_id,
                Inventory.ingredient_name.ilike(name_clean),
            )
        )
        return self.db.scalars(stmt).first()
