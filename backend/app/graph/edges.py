import logging

from langgraph.constants import END

from app.graph.state import GraphState

logger = logging.getLogger(__name__)


def should_continue_initialization(state: GraphState) -> str:
    """Conditional edge after initialization_node."""
    status = state.get("current_status", "")
    errors = state.get("errors", [])

    if status == "FAILED" or len(errors) > 0:
        logger.error("Initialization failed -> Routing to fail_order_node")
        return "fail_order_node"

    logger.info("Routing from initialization_node -> planner_node")
    return "planner_node"


def should_continue_planner(state: GraphState) -> str:
    """Conditional edge after planner_node."""
    errors = state.get("errors", [])
    retry_count = state.get("planner_retry_count", 0)

    if not errors or (len(errors) > 0 and state.get("recipe") is not None):
        logger.info("Routing from planner_node -> inventory_node")
        return "inventory_node"

    if retry_count < 3:
        logger.warning("Retrying planner_node | attempt=%s/3", retry_count + 1)
        return "planner_node"

    logger.error("Planner retries exceeded (3/3) -> Routing to fail_order_node")
    return "fail_order_node"


def should_continue_inventory(state: GraphState) -> str:
    """Conditional edge after inventory_node (No retries for financial/inventory operations)."""
    status = state.get("current_status", "")
    if status == "FAILED":
        logger.error("Inventory/Shopping failed -> Routing to fail_order_node")
        return "fail_order_node"

    logger.info("Routing from inventory_node -> cook_node")
    return "cook_node"


def should_continue_cook(state: GraphState) -> str:
    """Conditional edge after cook_node."""
    status = state.get("current_status", "")
    retry_count = state.get("cook_retry_count", 0)

    if status != "FAILED" and state.get("cooking_session") is not None:
        logger.info("Routing from cook_node -> judge_node")
        return "judge_node"

    if retry_count < 2:
        logger.warning("Retrying cook_node | attempt=%s/2", retry_count + 1)
        return "cook_node"

    logger.error("Cook retries exceeded (2/2) -> Routing to fail_order_node")
    return "fail_order_node"


def should_continue_judge(state: GraphState) -> str:
    """Conditional edge after judge_node."""
    status = state.get("current_status", "")
    retry_count = state.get("judge_retry_count", 0)

    if status != "FAILED" and state.get("judge_review") is not None:
        logger.info("Routing from judge_node -> reward_node")
        return "reward_node"

    if retry_count < 2:
        logger.warning("Retrying judge_node | attempt=%s/2", retry_count + 1)
        return "judge_node"

    logger.error("Judge retries exceeded (2/2) -> Routing to fail_order_node")
    return "fail_order_node"


def should_continue_reward(state: GraphState) -> str:
    """Conditional edge after reward_node."""
    status = state.get("current_status", "")
    if status == "COMPLETED":
        logger.info("Reward completed -> Routing to persistence_node")
        return "persistence_node"

    logger.error("Reward node failed -> Routing to fail_order_node")
    return "fail_order_node"
