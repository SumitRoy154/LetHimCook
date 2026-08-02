import logging
from functools import partial
from typing import Any

from langgraph.constants import END
# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph
from sqlalchemy.orm import Session

from app.graph.edges import (
    should_continue_cook,
    should_continue_initialization,
    should_continue_inventory,
    should_continue_judge,
    should_continue_planner,
    should_continue_reward,
)
from app.graph.nodes import (
    cook_node,
    fail_order_node,
    initialization_node,
    inventory_node,
    judge_node,
    persistence_node,
    planner_node,
    reward_node,
)
from app.graph.state import GraphState

logger = logging.getLogger(__name__)


def build_cooking_graph(db: Session, mock: bool = False) -> Any:
    """Build and compile the extended LangGraph StateGraph connecting real AI providers or Mock fallbacks."""
    workflow = StateGraph(GraphState)

    # Bind db session and mock flag to node functions
    bound_init = partial(initialization_node, db=db)
    bound_planner = partial(planner_node, db=db, mock=mock)
    bound_inventory = partial(inventory_node, db=db)
    bound_cook = partial(cook_node, db=db, mock=mock)
    bound_judge = partial(judge_node, db=db, mock=mock)
    bound_reward = partial(reward_node, db=db)
    bound_persistence = partial(persistence_node, db=db)
    bound_fail = partial(fail_order_node, db=db)

    # 1. Add Nodes
    workflow.add_node("initialization_node", bound_init)
    workflow.add_node("planner_node", bound_planner)
    workflow.add_node("inventory_node", bound_inventory)
    workflow.add_node("cook_node", bound_cook)
    workflow.add_node("judge_node", bound_judge)
    workflow.add_node("reward_node", bound_reward)
    workflow.add_node("persistence_node", bound_persistence)
    workflow.add_node("fail_order_node", bound_fail)

    # 2. Set Entry Point
    workflow.set_entry_point("initialization_node")

    # 3. Add Conditional Edges
    workflow.add_conditional_edges(
        "initialization_node",
        should_continue_initialization,
        {
            "planner_node": "planner_node",
            "fail_order_node": "fail_order_node",
        },
    )

    workflow.add_conditional_edges(
        "planner_node",
        should_continue_planner,
        {
            "inventory_node": "inventory_node",
            "planner_node": "planner_node",
            "fail_order_node": "fail_order_node",
        },
    )

    workflow.add_conditional_edges(
        "inventory_node",
        should_continue_inventory,
        {
            "cook_node": "cook_node",
            "fail_order_node": "fail_order_node",
        },
    )

    workflow.add_conditional_edges(
        "cook_node",
        should_continue_cook,
        {
            "judge_node": "judge_node",
            "cook_node": "cook_node",
            "fail_order_node": "fail_order_node",
        },
    )

    workflow.add_conditional_edges(
        "judge_node",
        should_continue_judge,
        {
            "reward_node": "reward_node",
            "judge_node": "judge_node",
            "fail_order_node": "fail_order_node",
        },
    )

    workflow.add_conditional_edges(
        "reward_node",
        should_continue_reward,
        {
            "persistence_node": "persistence_node",
            "fail_order_node": "fail_order_node",
        },
    )

    workflow.add_edge("persistence_node", END)
    workflow.add_edge("fail_order_node", END)

    # Compile graph
    compiled_graph = workflow.compile()
    logger.info("Extended LangGraph orchestrator graph compiled successfully (mock=%s).", mock)
    return compiled_graph


def get_graph_visualization() -> str:
    """Return Mermaid diagram string for extended graph visualization."""
    return """graph TD
    __start__([Start]) --> initialization_node[Initialization Node]
    initialization_node -->|Success| planner_node[Planner Node]
    initialization_node -->|Fail| fail_order_node[Fail Order Node]

    planner_node -->|Success| inventory_node[Inventory Node]
    planner_node -->|Retry < 3| planner_node
    planner_node -->|Fail >= 3| fail_order_node
    
    inventory_node -->|Success| cook_node[Cook Node]
    inventory_node -->|Fail| fail_order_node
    
    cook_node -->|Success| judge_node[Judge Node]
    cook_node -->|Retry < 2| cook_node
    cook_node -->|Fail >= 2| fail_order_node
    
    judge_node -->|Success| reward_node[Reward Node]
    judge_node -->|Retry < 2| judge_node
    judge_node -->|Fail >= 2| fail_order_node
    
    reward_node -->|Success| persistence_node[Persistence Node]
    reward_node -->|Fail| fail_order_node

    persistence_node --> __end__([End: COMPLETED])
    fail_order_node --> __end__([End: FAILED])
"""
