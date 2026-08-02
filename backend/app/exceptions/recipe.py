from app.exceptions.base import BusinessException


class RecipeException(BusinessException):
    """Base exception for recipe domain errors."""
    pass


class RecipeNotFoundException(RecipeException):
    """Raised when a recipe is not found in the recipe repository/cache."""
    def __init__(self, message: str = "Recipe not found"):
        super().__init__(message)


class RecipeAlreadyExistsException(RecipeException):
    """Raised when a recipe for a dish name already exists."""
    def __init__(self, message: str = "Recipe already exists"):
        super().__init__(message)
