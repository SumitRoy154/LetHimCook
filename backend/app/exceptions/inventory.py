from app.exceptions.base import BusinessException


class InventoryException(BusinessException):
    """Base exception for inventory domain errors."""
    pass


class IngredientNotFoundException(InventoryException):
    """Raised when an ingredient item is not found in inventory."""
    def __init__(self, message: str = "Ingredient not found"):
        super().__init__(message)


class IngredientAlreadyExistsException(InventoryException):
    """Raised when an ingredient already exists in inventory."""
    def __init__(self, message: str = "Ingredient already exists"):
        super().__init__(message)


class InsufficientIngredientException(InventoryException):
    """Raised when available ingredient quantity is insufficient."""
    def __init__(self, message: str = "Insufficient ingredient quantity"):
        super().__init__(message)
