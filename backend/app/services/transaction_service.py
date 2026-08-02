import logging
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.transaction_repo import TransactionRepository

logger = logging.getLogger(__name__)


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.transaction_repo = TransactionRepository(db)

    def create_transaction(
        self,
        wallet_id: int,
        amount: Decimal,
        transaction_type: str,
        description: Optional[str] = None,
    ) -> Transaction:
        """Create and log a wallet transaction entry (DEBIT / CREDIT / REWARD / DEPOSIT)."""
        tx = Transaction(
            wallet_id=wallet_id,
            amount=amount,
            transaction_type=transaction_type.upper(),
            description=description,
        )
        created_tx = self.transaction_repo.create(tx)
        logger.info(
            "Transaction recorded | wallet_id=%s, amount=%s, type=%s, tx_id=%s",
            wallet_id,
            amount,
            transaction_type,
            created_tx.id,
        )
        return created_tx

    def get_wallet_statement(self, wallet_id: int, skip: int = 0, limit: int = 50) -> List[Transaction]:
        """Fetch transaction history statement for a specific wallet."""
        return self.transaction_repo.get_by_wallet_id(wallet_id, skip=skip, limit=limit)

    def get_transaction_history(self, wallet_id: int, skip: int = 0, limit: int = 50) -> List[Transaction]:
        """Alias method for retrieving wallet transaction history."""
        return self.get_wallet_statement(wallet_id, skip=skip, limit=limit)
