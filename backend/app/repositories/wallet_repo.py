from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.repositories.base import BaseRepository


class WalletRepository(BaseRepository[Wallet]):
    def __init__(self, db: Session):
        super().__init__(Wallet, db)

    def get_by_user_id(self, user_id: int) -> Optional[Wallet]:
        stmt = select(Wallet).where(Wallet.user_id == user_id)
        return self.db.scalars(stmt).first()
