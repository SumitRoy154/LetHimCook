from app.exceptions.base import BusinessException


class TransactionException(BusinessException):
    """Base exception for transaction logging domain errors."""
    pass
