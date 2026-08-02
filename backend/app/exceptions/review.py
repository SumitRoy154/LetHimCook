from app.exceptions.base import BusinessException


class ReviewException(BusinessException):
    """Base exception for review memory domain errors."""
    pass


class ReviewNotFoundException(ReviewException):
    """Raised when a review is not found for an order."""
    def __init__(self, message: str = "Review not found"):
        super().__init__(message)
