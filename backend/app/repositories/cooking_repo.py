from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cooking import CookingSession
from app.repositories.base import BaseRepository


class CookingSessionRepository(BaseRepository[CookingSession]):
    def __init__(self, db: Session):
        super().__init__(CookingSession, db)

    def get_by_order_id(self, order_id: int) -> Optional[CookingSession]:
        stmt = select(CookingSession).where(CookingSession.order_id == order_id)
        return self.db.scalars(stmt).first()
