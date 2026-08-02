from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, db: Session):
        super().__init__(Transaction, db)

    def get_by_wallet_id(self, wallet_id: int, skip: int = 0, limit: int = 50) -> List[Transaction]:
        stmt = (
            select(Transaction)
            .where(Transaction.wallet_id == wallet_id)
            .order_by(Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
