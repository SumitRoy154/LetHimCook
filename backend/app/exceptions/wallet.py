from app.exceptions.base import BusinessException


class WalletException(BusinessException):
    """Base exception for wallet domain errors."""
    pass


class InsufficientBalanceException(WalletException):
    """Raised when debit amount exceeds available wallet balance."""
    def __init__(self, message: str = "Insufficient wallet balance"):
        super().__init__(message)


class WalletNotFoundException(WalletException):
    """Raised when wallet entity is missing."""
    def __init__(self, message: str = "Wallet not found"):
        super().__init__(message)
