import json
import logging
from typing import Any, Dict, Optional

from app.agents.base.base_agent import BaseAgent
from app.agents.providers.base_provider import LLMProvider
from app.agents.providers.factory import ProviderFactory
from app.schemas.agent import JudgeOutput

logger = logging.getLogger(__name__)


class JudgeAgent(BaseAgent[JudgeOutput]):
    """Judge Agent: Evaluates completed cooking session against recipe and generates review ratings."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        resolved_provider = provider or ProviderFactory.get_provider_for_role("judge")
        super().__init__(
            role_name="Judge",
            prompt_filename="judge.md",
            output_schema=JudgeOutput,
            provider=resolved_provider,
        )

    def prepare_input(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        dish_name = str(payload.get("dish_name", "")).strip()
        recipe_json = payload.get("recipe_json", {})
        cooking_json = payload.get("cooking_json", {})

        if not dish_name:
            raise ValueError("JudgeAgent payload requires 'dish_name'.")

        return {
            "dish_name": dish_name,
            "recipe_json": json.dumps(recipe_json, indent=2, default=str),
            "cooking_json": json.dumps(cooking_json, indent=2, default=str),
        }
