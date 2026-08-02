import logging
from typing import Any, Dict, Optional

from app.agents.base.base_agent import BaseAgent
from app.agents.providers.base_provider import LLMProvider
from app.agents.providers.factory import ProviderFactory
from app.schemas.agent import PlannerOutput

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent[PlannerOutput]):
    """Planner Agent: Decomposes a dish name into required ingredients and recipe steps."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        resolved_provider = provider or ProviderFactory.get_provider_for_role("planner")
        super().__init__(
            role_name="Planner",
            prompt_filename="planner.md",
            output_schema=PlannerOutput,
            provider=resolved_provider,
        )

    def prepare_input(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        dish_name = str(payload.get("dish_name", "")).strip()
        if not dish_name:
            raise ValueError("PlannerAgent payload requires 'dish_name'.")
        return {"dish_name": dish_name}
