from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.review import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, db: Session):
        super().__init__(Review, db)

    def get_by_order_id(self, order_id: int) -> Optional[Review]:
        stmt = select(Review).where(Review.order_id == order_id)
        return self.db.scalars(stmt).first()
