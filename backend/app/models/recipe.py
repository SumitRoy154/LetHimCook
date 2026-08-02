from typing import Any, Dict, Optional

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Recipe(Base, TimestampMixin):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dish_name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    recipe_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    ingredients_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    estimated_cooking_time: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
