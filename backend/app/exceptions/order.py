from app.exceptions.base import BusinessException


class OrderException(BusinessException):
    """Base exception for order domain errors."""
    pass


class OrderNotFoundException(OrderException):
    """Raised when an order entity is not found."""
    def __init__(self, message: str = "Order not found"):
        super().__init__(message)


class InvalidOrderStateException(OrderException):
    """Raised when an illegal order status transition is attempted."""
    def __init__(self, message: str = "Invalid order state transition"):
        super().__init__(message)
