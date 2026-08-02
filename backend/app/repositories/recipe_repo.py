from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.recipe import Recipe
from app.repositories.base import BaseRepository


class RecipeRepository(BaseRepository[Recipe]):
    def __init__(self, db: Session):
        super().__init__(Recipe, db)

    def get_by_dish_name(self, dish_name: str) -> Optional[Recipe]:
        stmt = select(Recipe).where(Recipe.dish_name == dish_name)
        return self.db.scalars(stmt).first()
