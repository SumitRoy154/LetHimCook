import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.agents import CookAgent, JudgeAgent, PlannerAgent
from app.agents.providers.mock_provider import MockProvider
from app.graph.state import GraphState
from app.repositories import OrderRepository, UserRepository
from app.services import (
    InventoryService,
    OrderService,
    PersistenceService,
    RecipeService,
    ReviewMemoryService,
    ShoppingService,
    TransactionService,
    WalletService,
)

logger = logging.getLogger(__name__)


def initialization_node(state: GraphState, db: Session) -> Dict[str, Any]:
    """Initialization Node (No LLM): Prepares workflow, validates user/order/wallet/inventory, and sets PENDING state."""
    logger.info("Entering initialization_node for user_id=%s, order_id=%s", state.get("user_id"), state.get("order_id"))
    user_id = state.get("user_id")
    order_id = state.get("order_id")
    start_dt = datetime.now(timezone.utc)
    timestamp = start_dt.isoformat()

    user_repo = UserRepository(db)
    order_repo = OrderRepository(db)
    wallet_service = WalletService(db)
    inventory_service = InventoryService(db)

    try:
        # 1. Validate User exists
        user = user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"User #{user_id} not found in database.")

        # 2. Validate Order exists
        order = order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order #{order_id} not found in database.")

        # 3. Load Wallet Balance
        balance = wallet_service.get_balance(user_id)

        # 4. Load User Inventory
        inv_items = [
            {"ingredient_name": i.ingredient_name, "quantity": str(i.quantity), "unit": i.unit}
            for i in inventory_service.get_inventory(user_id)
        ]

        logger.info("Initialization completed successfully for order #%s", order_id)
        return {
            "dish_name": order.dish_name,
            "wallet_balance": balance,
            "inventory": inv_items,
            "recipe": None,
            "shopping_summary": None,
            "cooking_session": None,
            "judge_review": None,
            "bonus_coins": Decimal("0.00"),
            "planner_retry_count": 0,
            "cook_retry_count": 0,
            "judge_retry_count": 0,
            "current_status": "PENDING",
            "workflow_start_time": timestamp,
            "execution_logs": [
                f"[{timestamp}] Initialization Started.",
                f"[{timestamp}] Initialization Completed. User #{user_id} & Order #{order_id} validated. Balance: {balance} coins.",
            ],
        }

    except Exception as exc:
        db.rollback()
        logger.error("Initialization node failure: %s", exc)
        return {
            "current_status": "FAILED",
            "errors": [f"Initialization failed: {exc}"],
            "execution_logs": [
                f"[{timestamp}] Initialization Started.",
                f"[{timestamp}] Initialization Failure: {exc}",
            ],
        }


def planner_node(state: GraphState, db: Session) -> Dict[str, Any]:
    """Planner Node: Queries RecipeService cache or invokes PlannerAgent to generate recipe."""
    logger.info("Entering planner_node for order_id=%s, dish='%s'", state.get("order_id"), state.get("dish_name"))
    dish_name = state["dish_name"]
    retry_count = state.get("planner_retry_count", 0)

    recipe_service = RecipeService(db)
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        # 1. Search Recipe Cache first
        cached_recipe = recipe_service.search_recipe(dish_name)
        if cached_recipe:
            recipe_dict = {
                "dish_name": cached_recipe.dish_name,
                "ingredients": cached_recipe.ingredients_json.get("items", []),
                "recipe_steps": cached_recipe.recipe_json.get("steps", []),
                "estimated_cooking_time": cached_recipe.estimated_cooking_time,
            }
            logger.info("Using cached recipe for '%s'", dish_name)
            return {
                "recipe": recipe_dict,
                "current_status": "RECIPE_READY",
                "execution_logs": [f"[{timestamp}] Planner Node: Using cached recipe for '{dish_name}'."],
            }

        # 2. Cache miss -> Invoke PlannerAgent
        planner_agent = PlannerAgent()

        output = planner_agent.run({"dish_name": dish_name})
        recipe_dict = output.model_dump(mode="json")

        # Cache generated recipe
        recipe_service.create_recipe(
            dish_name=dish_name,
            recipe_json={"steps": recipe_dict["recipe_steps"]},
            ingredients_json={"items": recipe_dict["ingredients"]},
            estimated_cooking_time=recipe_dict["estimated_cooking_time"],
        )

        return {
            "recipe": recipe_dict,
            "current_status": "RECIPE_READY",
            "execution_logs": [f"[{timestamp}] Planner Node: Generated & cached recipe for '{dish_name}'."],
        }

    except Exception as exc:
        db.rollback()
        logger.error("Planner node failure: %s", exc)
        return {
            "planner_retry_count": retry_count + 1,
            "errors": [f"Planner node error: {exc}"],
            "execution_logs": [f"[{timestamp}] Planner Node Failure: {exc}"],
        }


def inventory_node(state: GraphState, db: Session) -> Dict[str, Any]:
    """Inventory Node (No LLM): Purchases missing items, debits wallet, updates inventory & order status."""
    logger.info("Entering inventory_node for order_id=%s", state.get("order_id"))
    user_id = state["user_id"]
    order_id = state["order_id"]
    recipe = state.get("recipe", {})
    ingredients = recipe.get("ingredients", [])
    timestamp = datetime.now(timezone.utc).isoformat()

    order_service = OrderService(db)
    shopping_service = ShoppingService(db)
    wallet_service = WalletService(db)
    inventory_service = InventoryService(db)
    order_repo = OrderRepository(db)

    try:
        order_service.update_status(order_id, "SHOPPING")
        summary = shopping_service.purchase_missing_items(user_id, order_id, ingredients)

        # Update order's total_cost in DB immediately
        order = order_repo.get_by_id(order_id)
        if order:
            order.total_cost = summary["total_cost"]
            order_repo.update(order)

        current_balance = wallet_service.get_balance(user_id)
        current_inv = [
            {"ingredient_name": i.ingredient_name, "quantity": str(i.quantity), "unit": i.unit}
            for i in inventory_service.get_inventory(user_id)
        ]

        return {
            "shopping_summary": summary,
            "inventory": current_inv,
            "wallet_balance": current_balance,
            "current_status": "SHOPPING_COMPLETED",
            "execution_logs": [
                f"[{timestamp}] Inventory Node: Shopping completed. Spent: {summary['total_cost']} coins. Balance: {current_balance} coins."
            ],
        }

    except Exception as exc:
        db.rollback()
        logger.error("Inventory node failure: %s", exc)
        return {
            "current_status": "FAILED",
            "errors": [f"Inventory node error: {exc}"],
            "execution_logs": [f"[{timestamp}] Inventory Node Failure: {exc}"],
        }


def cook_node(state: GraphState, db: Session) -> Dict[str, Any]:
    """Cook Node: Retrieves previous review suggestions, invokes CookAgent, and consumes recipe ingredients."""
    logger.info("Entering cook_node for order_id=%s", state.get("order_id"))
    user_id = state["user_id"]
    order_id = state["order_id"]
    dish_name = state["dish_name"]
    recipe = state.get("recipe", {})
    recipe_steps = recipe.get("recipe_steps", [])
    ingredients = recipe.get("ingredients", [])
    retry_count = state.get("cook_retry_count", 0)

    order_service = OrderService(db)
    review_memory = ReviewMemoryService(db)
    inventory_service = InventoryService(db)
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        order_service.update_status(order_id, "COOKING")
        prev_suggestions = review_memory.get_previous_suggestions(dish_name)

        current_inv = [
            {"ingredient_name": i.ingredient_name, "quantity": str(i.quantity), "unit": i.unit}
            for i in inventory_service.get_inventory(user_id)
        ]

        cook_agent = CookAgent()

        output = cook_agent.run({
            "dish_name": dish_name,
            "recipe_steps": recipe_steps,
            "available_inventory": current_inv,
            "previous_suggestions": prev_suggestions,
        })
        cook_dict = output.model_dump(mode="json")

        inventory_service.consume(user_id, ingredients)

        return {
            "cooking_session": cook_dict,
            "current_status": "COOKING_COMPLETED",
            "execution_logs": [
                f"[{timestamp}] Cook Node: Cooking completed ({len(cook_dict['cooking_steps'])} steps). Ingredients consumed."
            ],
        }

    except Exception as exc:
        db.rollback()
        logger.error("Cook node failure: %s", exc)
        return {
            "cook_retry_count": retry_count + 1,
            "errors": [f"Cook node error: {exc}"],
            "execution_logs": [f"[{timestamp}] Cook Node Failure: {exc}"],
        }


def judge_node(state: GraphState, db: Session) -> Dict[str, Any]:
    """Judge Node: Invokes JudgeAgent, evaluates dish telemetry, and persists feedback to ReviewMemoryService."""
    logger.info("Entering judge_node for order_id=%s", state.get("order_id"))
    order_id = state["order_id"]
    dish_name = state["dish_name"]
    recipe = state.get("recipe", {})
    cooking_session = state.get("cooking_session", {})
    retry_count = state.get("judge_retry_count", 0)

    order_service = OrderService(db)
    review_memory = ReviewMemoryService(db)
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        order_service.update_status(order_id, "JUDGING")

        judge_agent = JudgeAgent()

        output = judge_agent.run({
            "dish_name": dish_name,
            "recipe_json": recipe,
            "cooking_json": cooking_session,
        })
        judge_dict = output.model_dump(mode="json")
        score_val = Decimal(str(judge_dict.get("score", 8.5)))

        review_memory.store_review(
            order_id=order_id,
            score=score_val,
            review_text=judge_dict["review"],
            suggestions=judge_dict.get("suggestions"),
            bonus_coins=Decimal("0.00"),
        )

        return {
            "judge_review": judge_dict,
            "current_status": "JUDGING_COMPLETED",
            "execution_logs": [
                f"[{timestamp}] Judge Node: Evaluation completed | Score: {score_val}/10."
            ],
        }

    except Exception as exc:
        db.rollback()
        logger.error("Judge node failure: %s", exc)
        return {
            "judge_retry_count": retry_count + 1,
            "errors": [f"Judge node error: {exc}"],
            "execution_logs": [f"[{timestamp}] Judge Node Failure: {exc}"],
        }


def reward_node(state: GraphState, db: Session) -> Dict[str, Any]:
    """Reward Node: Invokes RewardAgent to dynamically calculate reward coins (Shopping Cost * 2), credits user wallet, logs transaction, and marks order COMPLETED."""
    logger.info("Entering reward_node for order_id=%s", state.get("order_id"))
    user_id = state["user_id"]
    order_id = state["order_id"]
    timestamp = datetime.now(timezone.utc).isoformat()

    wallet_service = WalletService(db)
    order_service = OrderService(db)
    order_repo = OrderRepository(db)
    from app.repositories.shopping_repo import ShoppingHistoryRepository
    shopping_repo = ShoppingHistoryRepository(db)
    from app.agents.reward import RewardAgent

    try:
        # 1. Obtain shopping cost from state or database
        shopping_summary = state.get("shopping_summary")
        shopping_cost = Decimal("0.00")

        if shopping_summary and "total_cost" in shopping_summary:
            shopping_cost = Decimal(str(shopping_summary["total_cost"]))
        else:
            # Fallback query from shopping history database
            history_records = shopping_repo.get_by_order_id(order_id)
            shopping_cost = sum((r.price for r in history_records), Decimal("0.00"))

        # 2. Invoke RewardAgent for dynamic calculation (Reward Coins = Shopping Cost * 2)
        reward_agent = RewardAgent()

        # Calculate reward deterministically using RewardAgent method
        reward_output = reward_agent.calculate_reward(shopping_cost)
        reward_coins = reward_output.reward_coins

        # 3. Credit wallet balance if reward > 0 and record transaction
        if reward_coins > Decimal("0.00"):
            wallet_service.credit(
                user_id=user_id,
                amount=reward_coins,
                description=f"Reward for Order #{order_id} ({reward_output.calculation_formula})",
            )

        # 4. Update order record in DB with reward_received & mark completed
        order = order_repo.get_by_id(order_id)
        if order:
            order.reward_received = reward_coins
            order.total_cost = shopping_cost
            order_repo.update(order)

        order_service.update_status(order_id, "COMPLETED")
        final_balance = wallet_service.get_balance(user_id)

        logger.info(
            "Reward Node Completed | order_id=%s, shopping_cost=%s, reward_coins=%s, final_balance=%s",
            order_id,
            shopping_cost,
            reward_coins,
            final_balance,
        )

        return {
            "bonus_coins": reward_coins,
            "wallet_balance": final_balance,
            "current_status": "COMPLETED",
            "execution_logs": [
                f"[{timestamp}] Reward Node: Calculated reward coins: {reward_coins} ({reward_output.calculation_formula}). Credited to wallet. Order #{order_id} COMPLETED. Final Balance: {final_balance} coins."
            ],
        }

    except Exception as exc:
        db.rollback()
        logger.error("Reward node failure: %s", exc)
        return {
            "current_status": "FAILED",
            "errors": [f"Reward node error: {exc}"],
            "execution_logs": [f"[{timestamp}] Reward Node Failure: {exc}"],
        }


def persistence_node(state: GraphState, db: Session) -> Dict[str, Any]:
    """Persistence Node (No LLM): Persists full workflow execution snapshot safely to database."""
    logger.info("Entering persistence_node for order_id=%s", state.get("order_id"))
    user_id = state.get("user_id")
    order_id = state.get("order_id")
    end_dt = datetime.now(timezone.utc)
    end_timestamp = end_dt.isoformat()

    persistence_service = PersistenceService(db)

    # Calculate execution duration
    duration_ms = None
    started_at_dt = None
    start_str = state.get("workflow_start_time")

    if start_str:
        try:
            started_at_dt = datetime.fromisoformat(start_str)
            duration_ms = int((end_dt - started_at_dt).total_seconds() * 1000)
        except Exception:
            pass

    # Build state snapshot
    snapshot = {
        "user_id": user_id,
        "order_id": order_id,
        "dish_name": state.get("dish_name"),
        "wallet_balance": str(state.get("wallet_balance", "0.00")),
        "bonus_coins": str(state.get("bonus_coins", "0.00")),
        "recipe": state.get("recipe"),
        "shopping_summary": state.get("shopping_summary"),
        "cooking_session": state.get("cooking_session"),
        "judge_review": state.get("judge_review"),
        "current_status": state.get("current_status"),
    }
    # Ensure nested Decimal objects in recipe/shopping_summary are converted to float/str
    snapshot_json_clean = json.loads(json.dumps(snapshot, default=str))

    record = persistence_service.save_execution(
        order_id=order_id,
        user_id=user_id,
        workflow_status=state.get("current_status", "COMPLETED"),
        started_at=started_at_dt,
        completed_at=end_dt,
        execution_time_ms=duration_ms,
        execution_logs=state.get("execution_logs", []),
        error_logs=state.get("errors", []),
        graph_state_snapshot=snapshot_json_clean,
        final_wallet_balance=state.get("wallet_balance"),
        bonus_coins=state.get("bonus_coins"),
    )

    exec_id = record.id if record else None

    return {
        "workflow_end_time": end_timestamp,
        "execution_duration_ms": duration_ms,
        "workflow_execution_id": exec_id,
        "graph_state_snapshot": snapshot,
        "execution_logs": [
            f"[{end_timestamp}] Persistence Started.",
            f"[{end_timestamp}] Persistence Completed. Audit record #{exec_id} saved (duration: {duration_ms}ms).",
        ],
    }


def fail_order_node(state: GraphState, db: Session) -> Dict[str, Any]:
    """Fail Order Node: Marks order as FAILED in database and halts workflow safely."""
    logger.warning("Entering fail_order_node for order_id=%s", state.get("order_id"))
    order_id = state.get("order_id")
    user_id = state.get("user_id")
    errors = state.get("errors", [])
    timestamp = datetime.now(timezone.utc).isoformat()

    if order_id:
        try:
            db.rollback()
            order_service = OrderService(db)
            order_service.update_status(order_id, "FAILED")
        except Exception as exc:
            logger.error("Error updating order to FAILED: %s", exc)

    # Optionally persist audit record for failure
    if user_id and order_id:
        try:
            persistence_service = PersistenceService(db)
            persistence_service.save_execution(
                order_id=order_id,
                user_id=user_id,
                workflow_status="FAILED",
                completed_at=datetime.now(timezone.utc),
                execution_logs=state.get("execution_logs", []),
                error_logs=errors,
                graph_state_snapshot={"errors": errors, "status": "FAILED"},
            )
        except Exception:
            pass

    return {
        "current_status": "FAILED",
        "execution_logs": [
            f"[{timestamp}] Workflow Aborted / Order #{order_id} FAILED | Reason: {'; '.join(errors)}"
        ],
    }
