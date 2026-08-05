import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agents.providers.factory import ProviderFactory
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.api import RecipeResponse
from app.services.recipe_service import RecipeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recipes", tags=["Recipes"])


class CravingSuggestionRequest(BaseModel):
    craving: str = Field(..., description="User's craving description or dish search query")


class DishOption(BaseModel):
    name: str = Field(..., description="Corrected or suggested dish name")
    description: str = Field(..., description="Short delicious description of the dish")
    emoji: str = Field(default="🍲", description="Emoji representation")


class CravingSuggestionResponse(BaseModel):
    suggestions: List[DishOption] = Field(..., description="List of 3-4 suggested dishes")


@router.post(
    "/suggest",
    response_model=CravingSuggestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI Dish Suggestions",
    description="Groq checks recipes DB table first for matches, then uses AI to suggest 3-4 dishes based on user craving.",
)
def suggest_dishes(
    payload: CravingSuggestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CravingSuggestionResponse:
    try:
        recipe_service = RecipeService(db)
        craving_text = payload.craving.strip()

        # 1. First check DB recipes table for matches
        db_recipes = recipe_service.recipe_repo.get_all(limit=50)
        db_match_names = [
            r.dish_name for r in db_recipes 
            if any(term in r.dish_name.lower() for term in craving_text.lower().split())
        ]

        # 2. Call Groq provider to generate suggestions
        groq_provider = ProviderFactory.get_provider_for_role("planner")
        
        prompt = f"""You are a culinary AI assistant. A user is expressing this craving or searching for a dish: "{craving_text}".

Database Context (recipes already in our system):
{json.dumps(db_match_names)}

Instructions:
1. Correct any spelling errors in the user's craving input.
2. Provide exactly 3 to 4 distinct, appetizing dish options.
3. If database recipes match the craving, prioritize including them.
4. Output MUST be valid JSON only matching this schema:
{{
  "suggestions": [
    {{ "name": "Dish Name", "description": "Short mouthwatering summary", "emoji": "🍲" }}
  ]
}}
"""
        raw_response = groq_provider.generate(prompt=prompt)
        
        # Clean JSON if markdown fences are returned
        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json.split("```json")[1].split("```")[0].strip()
        elif clean_json.startswith("```"):
            clean_json = clean_json.split("```")[1].split("```")[0].strip()

        parsed = json.loads(clean_json)
        return CravingSuggestionResponse.model_validate(parsed)

    except Exception as e:
        logger.exception("Error generating dish suggestions: %s", e)
        # Fallback response
        return CravingSuggestionResponse(suggestions=[
            DishOption(name=payload.craving.title(), description="Your requested custom dish.", emoji="🍳"),
            DishOption(name="Paneer Butter Masala", description="Rich and creamy paneer gravy.", emoji="🥘"),
            DishOption(name="Chicken Biryani", description="Fragrant basmati rice cooked with spices.", emoji="🍗"),
        ])


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
