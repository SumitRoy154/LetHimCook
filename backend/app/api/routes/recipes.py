import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.exceptions.base import BusinessException
from app.models.user import User
from app.schemas.api import RecipeResponse
from app.services.recipe_service import RecipeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get(
    "/{dish_name}",
    response_model=RecipeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Cached Recipe",
    description="Return cached recipe details for a dish if available.",
)
def get_cached_recipe(
    dish_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecipeResponse:
    try:
        recipe_service = RecipeService(db)
        recipe = recipe_service.search_recipe(dish_name)
        if not recipe:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cached recipe found for '{dish_name}'")
        return RecipeResponse.model_validate(recipe)
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting cached recipe: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")
