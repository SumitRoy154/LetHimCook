import logging
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.exceptions.wallet import InsufficientBalanceException, WalletNotFoundException
from app.models.wallet import Wallet
from app.repositories.wallet_repo import WalletRepository
from app.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


class WalletService:
    def __init__(self, db: Session):
        self.db = db
        self.wallet_repo = WalletRepository(db)
        self.tx_service = TransactionService(db)

    def _get_wallet_by_user(self, user_id: int) -> Wallet:
        wallet = self.wallet_repo.get_by_user_id(user_id)
        if not wallet:
            raise WalletNotFoundException(f"Wallet for user_id {user_id} does not exist.")
        return wallet

    def get_balance(self, user_id: int) -> Decimal:
        """Return the current balance for a user's wallet."""
        wallet = self._get_wallet_by_user(user_id)
        return wallet.balance

    def has_sufficient_balance(self, user_id: int, amount: Decimal) -> bool:
        """Check if user's wallet has at least amount available."""
        if amount < Decimal("0.00"):
            return False
        balance = self.get_balance(user_id)
        return balance >= amount

    def credit(self, user_id: int, amount: Decimal, description: Optional[str] = None) -> Wallet:
        """Credit coins to user's wallet and log transaction."""
        if amount <= Decimal("0.00"):
            raise ValueError("Credit amount must be greater than zero.")

        wallet = self._get_wallet_by_user(user_id)
        wallet.balance += amount
        updated_wallet = self.wallet_repo.update(wallet)

        self.tx_service.create_transaction(
            wallet_id=wallet.id,
            amount=amount,
            transaction_type="CREDIT",
            description=description or "Wallet credit",
        )

        logger.info(
            "Wallet credited | user_id=%s, amount=%s, new_balance=%s",
            user_id,
            amount,
            updated_wallet.balance,
        )
        return updated_wallet

    def debit(self, user_id: int, amount: Decimal, description: Optional[str] = None) -> Wallet:
        """Debit coins from user's wallet. Enforces non-negative balance rule."""
        if amount <= Decimal("0.00"):
            raise ValueError("Debit amount must be greater than zero.")

        wallet = self._get_wallet_by_user(user_id)

        if wallet.balance < amount:
            logger.warning(
                "Debit failed - Insufficient balance | user_id=%s, requested=%s, current=%s",
                user_id,
                amount,
                wallet.balance,
            )
            raise InsufficientBalanceException(
                f"Insufficient balance. Required: {amount}, Available: {wallet.balance}"
            )

        wallet.balance -= amount
        updated_wallet = self.wallet_repo.update(wallet)

        self.tx_service.create_transaction(
            wallet_id=wallet.id,
            amount=-amount,
            transaction_type="DEBIT",
            description=description or "Wallet debit",
        )

        logger.info(
            "Wallet debited | user_id=%s, amount=%s, new_balance=%s",
            user_id,
            amount,
            updated_wallet.balance,
        )
        return updated_wallet
