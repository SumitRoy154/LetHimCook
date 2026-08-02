from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.repositories.base import BaseRepository


class InventoryRepository(BaseRepository[Inventory]):
    def __init__(self, db: Session):
        super().__init__(Inventory, db)

    def get_by_user_id(self, user_id: int) -> List[Inventory]:
        stmt = select(Inventory).where(Inventory.user_id == user_id)
        return list(self.db.scalars(stmt).all())

    def get_user_ingredient(self, user_id: int, ingredient_name: str) -> Optional[Inventory]:
        stmt = select(Inventory).where(
            Inventory.user_id == user_id,
            Inventory.ingredient_name == ingredient_name,
        )
        return self.db.scalars(stmt).first()
