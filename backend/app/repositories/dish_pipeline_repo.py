from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dish_pipeline import DishIngredient, DishRecipe
from app.repositories.base import BaseRepository


class DishIngredientRepository(BaseRepository[DishIngredient]):
    def __init__(self, db: Session):
        super().__init__(DishIngredient, db)

    def get_by_order_id(self, order_id: int) -> Optional[DishIngredient]:
        stmt = select(DishIngredient).where(DishIngredient.order_id == order_id)
        return self.db.scalars(stmt).first()


class DishRecipeRepository(BaseRepository[DishRecipe]):
    def __init__(self, db: Session):
        super().__init__(DishRecipe, db)

    def get_by_order_id(self, order_id: int) -> Optional[DishRecipe]:
        stmt = select(DishRecipe).where(DishRecipe.order_id == order_id)
        return self.db.scalars(stmt).first()
