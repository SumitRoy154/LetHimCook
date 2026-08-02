import logging
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.exceptions.recipe import RecipeAlreadyExistsException, RecipeNotFoundException
from app.models.recipe import Recipe
from app.repositories.recipe_repo import RecipeRepository

logger = logging.getLogger(__name__)


class RecipeService:
    def __init__(self, db: Session):
        self.db = db
        self.recipe_repo = RecipeRepository(db)

    def search_recipe(self, dish_name: str) -> Optional[Recipe]:
        """Search for a cached recipe by dish name (used by Planner role)."""
        normalized_name = dish_name.lower().strip()
        recipe = self.recipe_repo.get_by_dish_name(normalized_name)
        if recipe:
            logger.info("Recipe cache hit | dish_name='%s', recipe_id=%s", normalized_name, recipe.id)
        else:
            logger.info("Recipe cache miss | dish_name='%s'", normalized_name)
        return recipe

    def create_recipe(
        self,
        dish_name: str,
        recipe_json: Dict[str, Any],
        ingredients_json: Dict[str, Any],
        estimated_cooking_time: Optional[int] = None,
    ) -> Recipe:
        """Create and cache a new dish recipe."""
        normalized_name = dish_name.lower().strip()

        if self.recipe_repo.get_by_dish_name(normalized_name):
            raise RecipeAlreadyExistsException(f"Recipe for '{dish_name}' already exists in cache.")

        new_recipe = Recipe(
            dish_name=normalized_name,
            recipe_json=recipe_json,
            ingredients_json=ingredients_json,
            estimated_cooking_time=estimated_cooking_time,
        )
        created_recipe = self.recipe_repo.create(new_recipe)
        logger.info("Recipe created & cached | dish_name='%s', recipe_id=%s", normalized_name, created_recipe.id)
        return created_recipe

    def update_recipe(
        self,
        recipe_id: int,
        recipe_json: Optional[Dict[str, Any]] = None,
        ingredients_json: Optional[Dict[str, Any]] = None,
        estimated_cooking_time: Optional[int] = None,
    ) -> Recipe:
        """Update an existing cached recipe."""
        recipe = self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(f"Recipe #{recipe_id} not found.")

        if recipe_json is not None:
            recipe.recipe_json = recipe_json
        if ingredients_json is not None:
            recipe.ingredients_json = ingredients_json
        if estimated_cooking_time is not None:
            recipe.estimated_cooking_time = estimated_cooking_time

        updated_recipe = self.recipe_repo.update(recipe)
        logger.info("Recipe updated | recipe_id=%s", recipe_id)
        return updated_recipe

    def delete_recipe(self, recipe_id: int) -> None:
        """Delete a recipe from cache."""
        recipe = self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise RecipeNotFoundException(f"Recipe #{recipe_id} not found.")

        self.recipe_repo.delete(recipe)
        logger.info("Recipe deleted | recipe_id=%s", recipe_id)
