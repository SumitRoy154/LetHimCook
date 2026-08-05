import json
import logging
from typing import Any, Dict, Optional

from app.agents.base.base_agent import BaseAgent
from app.agents.providers.base_provider import LLMProvider
from app.agents.providers.factory import ProviderFactory
from app.schemas.agent import CookOutput

logger = logging.getLogger(__name__)


class CookAgent(BaseAgent[CookOutput]):
    """Cook Agent (Claude): Generates recipe JSON and executes cooking steps based on dish_ingredients."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        resolved_provider = provider or ProviderFactory.get_provider_for_role("cook")
        super().__init__(
            role_name="Cook",
            prompt_filename="cook.md",
            output_schema=CookOutput,
            provider=resolved_provider,
        )

    def prepare_input(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        dish_name = str(payload.get("dish_name", "")).strip()
        dish_ingredients = payload.get("dish_ingredients", [])
        inventory = payload.get("available_inventory", [])
        suggestions = payload.get("previous_suggestions", [])

        if not dish_name:
            raise ValueError("CookAgent payload requires 'dish_name'.")

        return {
            "dish_name": dish_name,
            "dish_ingredients": json.dumps(dish_ingredients, indent=2, default=str),
            "available_inventory": json.dumps(inventory, indent=2, default=str),
            "previous_suggestions": json.dumps(suggestions, indent=2, default=str),
        }
