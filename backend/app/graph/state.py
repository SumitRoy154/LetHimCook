from decimal import Decimal
from typing import Annotated, Any, Dict, List, Optional, TypedDict


def add_logs(left: List[str], right: List[str]) -> List[str]:
    """Reducer function appending execution log entries."""
    return left + right


def add_errors(left: List[str], right: List[str]) -> List[str]:
    """Reducer function appending error messages."""
    return left + right


class GraphState(TypedDict, total=False):
    """Shared state dictionary passed across all nodes in the LangGraph workflow."""

    user_id: int
    order_id: int
    dish_name: str
    wallet_balance: Decimal
    inventory: List[Dict[str, Any]]
    recipe: Optional[Dict[str, Any]]
    shopping_summary: Optional[Dict[str, Any]]
    cooking_session: Optional[Dict[str, Any]]
    judge_review: Optional[Dict[str, Any]]
    bonus_coins: Decimal
    current_status: str
    planner_retry_count: int
    cook_retry_count: int
    judge_retry_count: int
    errors: Annotated[List[str], add_errors]
    execution_logs: Annotated[List[str], add_logs]
    timestamps: Dict[str, str]

    # Added in Phase 6 Extension
    workflow_start_time: Optional[str]
    workflow_end_time: Optional[str]
    execution_duration_ms: Optional[int]
    workflow_execution_id: Optional[int]
    graph_state_snapshot: Optional[Dict[str, Any]]
