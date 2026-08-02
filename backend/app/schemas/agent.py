from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class IngredientItem(BaseModel):
    name: str = Field(..., description="Ingredient name")
    quantity: Decimal = Field(..., description="Quantity needed")
    unit: str = Field(..., description="Measurement unit (e.g. g, kg, pcs, tbsp)")
    price: Decimal = Field(Decimal("5.00"), description="Estimated unit purchase price in coins")


class PlannerOutput(BaseModel):
    dish_name: str = Field(..., description="Name of the dish")
    ingredients: List[IngredientItem] = Field(..., description="List of required ingredients")
    recipe_steps: List[str] = Field(..., description="Step-by-step cooking instructions")
    estimated_cooking_time: int = Field(15, description="Estimated cooking time in minutes")


class CookingStepItem(BaseModel):
    step_number: int = Field(..., description="Step index")
    action: str = Field(..., description="Cooking action executed")
    status: str = Field("COMPLETED", description="Step status")
    duration_seconds: int = Field(60, description="Duration of step in seconds")


class CookOutput(BaseModel):
    cooking_steps: List[CookingStepItem] = Field(..., description="Executed cooking steps")
    step_telemetry: List[Dict[str, Any]] = Field(default_factory=list, description="Telemetry logs")
    status: str = Field("COMPLETED", description="Overall cooking session status")


class JudgeOutput(BaseModel):
    score: Decimal = Field(..., description="Dish score out of 10.00")
    review: str = Field(..., description="Detailed review and feedback")
    suggestions: Optional[str] = Field(None, description="Suggestions for future cooking runs")
    bonus_coins: Optional[Decimal] = Field(Decimal("0.00"), description="Legacy field for bonus coins")
