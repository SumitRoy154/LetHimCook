from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.agents.base.base_agent import BaseAgent
from app.agents.providers.base_provider import LLMProvider
from app.agents.providers.factory import ProviderFactory


class RewardOutput(BaseModel):
    shopping_cost: Decimal = Field(..., description="Actual shopping cost incurred")
    reward_multiplier: Decimal = Field(Decimal("2.00"), description="Multiplier applied to shopping cost")
    reward_coins: Decimal = Field(..., description="Calculated reward coins (Shopping Cost * 2)")
    calculation_formula: str = Field(..., description="Formula used for reward calculation")


class RewardAgent(BaseAgent[RewardOutput]):
    """Reward Agent: Computes dynamic reward coins based on actual shopping cost (Shopping Cost * 2)."""

    def __init__(self, provider: Optional[LLMProvider] = None):
        resolved_provider = provider or ProviderFactory.get_provider_for_role("reward")
        super().__init__(
            role_name="Reward",
            prompt_filename="reward.md",
            output_schema=RewardOutput,
            provider=resolved_provider,
        )

    def prepare_input(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        shopping_cost = Decimal(str(payload.get("shopping_cost", "0.00")))
        return {
            "shopping_cost": str(shopping_cost),
        }

    def calculate_reward(self, shopping_cost: Decimal) -> RewardOutput:
        """Deterministic calculation of reward coins (Shopping Cost * 2)."""
        cost = Decimal(str(shopping_cost))
        multiplier = Decimal("2.00")
        reward = cost * multiplier
        return RewardOutput(
            shopping_cost=cost,
            reward_multiplier=multiplier,
            reward_coins=reward,
            calculation_formula=f"Reward Coins = {cost} * {multiplier} = {reward}",
        )
