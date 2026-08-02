from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.shopping import ShoppingHistory
from app.repositories.base import BaseRepository


class ShoppingHistoryRepository(BaseRepository[ShoppingHistory]):
    def __init__(self, db: Session):
        super().__init__(ShoppingHistory, db)

    def get_by_order_id(self, order_id: int) -> List[ShoppingHistory]:
        stmt = select(ShoppingHistory).where(ShoppingHistory.order_id == order_id)
        return list(self.db.scalars(stmt).all())
