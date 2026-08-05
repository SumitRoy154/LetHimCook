import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.agents.cook import CookAgent
from app.agents.judge import JudgeAgent
from app.agents.planner import PlannerAgent
from app.graph.state import GraphState
from app.repositories.dish_pipeline_repo import (
    DishIngredientRepository,
    DishRecipeRepository,
)
from app.repositories.inventory_repo import InventoryRepository
from app.repositories.order_repo import OrderRepository
from app.repositories.review_repo import ReviewRepository
from app.services.inventory_service import InventoryService
from app.services.order_service import OrderService
from app.services.review_memory_service import ReviewMemoryService
from app.services.shopping_service import ShoppingService
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)


def initialization_node(state: GraphState, db: Session) -> Dict[str, Any]:
    """Initialization Node: Validates order and loads initial state."""
    logger.info("Entering initialization_node for order_id=%s", state.get("order_id"))
    user_id = state["user_id"]
    order_id = state["order_id"]
    timestamp = datetime.now(timezone.utc).isoformat()

    wallet_service = WalletService(db)
    inventory_service = InventoryService(db)
    order_repo = OrderRepository(db)

    try:
        # 1. Update Order Status
        order_service = OrderService(db)
        order_service.update_status(order_id, "PENDING")

        # 2. Validate Order exists
        order = order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order #{order_id} not found in database.")

        # 3. Load Wallet Balance
        balance = wallet_service.get_balance(user_id)

        # 4. Load User Inventory
        inv_items = [
            {"ingredient_name": i["ingredient_name"], "quantity": str(i["quantity"]), "unit": i["unit"]}
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
    """Planner Node (Groq): Generates ingredients JSON, updates inventories catalog, and stores dish_ingredients."""
    logger.info("Entering planner_node for order_id=%s, dish='%s'", state.get("order_id"), state.get("dish_name"))
    order_id = state["order_id"]
    dish_name = state["dish_name"]
    retry_count = state.get("planner_retry_count", 0)
    timestamp = datetime.now(timezone.utc).isoformat()

    inventory_service = InventoryService(db)
    dish_ing_repo = DishIngredientRepository(db)

    try:
        planner_agent = PlannerAgent()
        output = planner_agent.run({"dish_name": dish_name})
        ingredients_list = output.ingredients

        # 1. Update/Add items in global inventories catalog
        for ing in ingredients_list:
            inventory_service.get_or_create_global_item(
                ingredient_name=ing.name,
                unit=ing.unit,
                purchase_price=ing.price,
            )

        # 2. Persist in dish_ingredients table
        dish_ing_dict = {
            "dish_name": dish_name,
            "ingredients": [i.model_dump(mode="json") for i in ingredients_list],
        }
        existing_record = dish_ing_repo.get_by_order_id(order_id)
        if existing_record:
            existing_record.ingredients = dish_ing_dict["ingredients"]
            dish_ing_repo.update(existing_record)
        else:
            from app.models.dish_pipeline import DishIngredient
            new_record = DishIngredient(
                order_id=order_id,
                dish_name=dish_name,
                ingredients=dish_ing_dict["ingredients"],
            )
            dish_ing_repo.create(new_record)

        return {
            "recipe": {"dish_name": dish_name, "ingredients": dish_ing_dict["ingredients"]},
            "current_status": "RECIPE_READY",
            "execution_logs": [f"[{timestamp}] Planner Node (Groq): Generated ingredients and stored in dish_ingredients table."],
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
    """Inventory Node: Compares dish_ingredients with user_inventories, logs shopping_histories, updates user stock, and debits wallet."""
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
            {"ingredient_name": i["ingredient_name"], "quantity": str(i["quantity"]), "unit": i["unit"]}
            for i in inventory_service.get_inventory(user_id)
        ]

        return {
            "shopping_summary": summary,
            "inventory": current_inv,
            "wallet_balance": current_balance,
            "current_status": "SHOPPING_COMPLETED",
            "execution_logs": [
                f"[{timestamp}] Inventory Node: Shopping completed. Total Cost: {summary['total_cost']} coins. Updated wallet balance: {current_balance} coins."
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
    """Cook Node (Claude): Uses dish_ingredients to generate recipe_steps, stores in dish_recipes table, and consumes ingredients."""
    logger.info("Entering cook_node for order_id=%s", state.get("order_id"))
    user_id = state["user_id"]
    order_id = state["order_id"]
    dish_name = state["dish_name"]
    recipe = state.get("recipe", {})
    ingredients = recipe.get("ingredients", [])
    retry_count = state.get("cook_retry_count", 0)
    timestamp = datetime.now(timezone.utc).isoformat()

    order_service = OrderService(db)
    review_memory = ReviewMemoryService(db)
    inventory_service = InventoryService(db)
    dish_ing_repo = DishIngredientRepository(db)
    dish_rec_repo = DishRecipeRepository(db)

    try:
        order_service.update_status(order_id, "COOKING")
        prev_suggestions = review_memory.get_previous_suggestions(dish_name)

        current_inv = [
            {"ingredient_name": i["ingredient_name"], "quantity": str(i["quantity"]), "unit": i["unit"]}
            for i in inventory_service.get_inventory(user_id)
        ]

        # Fetch dish_ingredients record
        dish_ing_record = dish_ing_repo.get_by_order_id(order_id)
        dish_ing_data = dish_ing_record.ingredients if dish_ing_record else ingredients

        cook_agent = CookAgent()
        output = cook_agent.run({
            "dish_name": dish_name,
            "dish_ingredients": dish_ing_data,
            "available_inventory": current_inv,
            "previous_suggestions": prev_suggestions,
        })
        cook_dict = output.model_dump(mode="json")

        # Save to dish_recipes table
        if dish_ing_record:
            from app.models.dish_pipeline import DishRecipe
            existing_recipe = dish_rec_repo.get_by_order_id(order_id)
            recipe_payload = {
                "recipe_steps": cook_dict.get("recipe_steps", []),
                "cooking_steps": cook_dict.get("cooking_steps", []),
            }
            if existing_recipe:
                existing_recipe.recipe = recipe_payload
                dish_rec_repo.update(existing_recipe)
            else:
                new_recipe = DishRecipe(
                    order_id=order_id,
                    dish_ingredient_id=dish_ing_record.id,
                    dish_name=dish_name,
                    recipe=recipe_payload,
                )
                dish_rec_repo.create(new_recipe)

        # Consumes recipe ingredients from user stock
        inventory_service.consume(user_id, ingredients)

        # Combine recipe details for state
        combined_recipe = {
            "dish_name": dish_name,
            "ingredients": ingredients,
            "recipe_steps": cook_dict.get("recipe_steps", []),
        }

        return {
            "recipe": combined_recipe,
            "cooking_session": cook_dict,
            "current_status": "COOKING_COMPLETED",
            "execution_logs": [
                f"[{timestamp}] Cook Node (Claude): Recipe JSON stored in dish_recipes table & cooking execution completed."
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
    """Judge Node (Gemini): Evaluates dish execution, generates review and random bonus_coins (< 30), stores in reviews table."""
    logger.info("Entering judge_node for order_id=%s", state.get("order_id"))
    order_id = state["order_id"]
    dish_name = state["dish_name"]
    recipe = state.get("recipe", {})
    cooking_session = state.get("cooking_session", {})
    shopping_summary = state.get("shopping_summary", {})
    retry_count = state.get("judge_retry_count", 0)
    timestamp = datetime.now(timezone.utc).isoformat()

    order_service = OrderService(db)
    review_repo = ReviewRepository(db)

    try:
        order_service.update_status(order_id, "JUDGING")
        total_cost = Decimal(str(shopping_summary.get("total_cost", "0.00")))

        judge_agent = JudgeAgent()
        output = judge_agent.run({
            "dish_name": dish_name,
            "total_cost": str(total_cost),
            "recipe_json": recipe,
            "cooking_json": cooking_session,
        })
        judge_dict = output.model_dump(mode="json")
        score_val = Decimal(str(judge_dict.get("score", 8.5)))
        bonus_coins_val = Decimal(str(judge_dict.get("bonus_coins", 10.0)))
        if bonus_coins_val >= Decimal("30.00"):
            bonus_coins_val = Decimal("15.00")

        # Save review into reviews table
        existing_review = review_repo.get_by_order_id(order_id)
        if existing_review:
            existing_review.score = score_val
            existing_review.review = judge_dict["review"]
            existing_review.suggestions = judge_dict.get("suggestions")
            existing_review.bonus_coins = bonus_coins_val
            review_repo.update(existing_review)
        else:
            from app.models.review import Review
            new_review = Review(
                order_id=order_id,
                score=score_val,
                review=judge_dict["review"],
                suggestions=judge_dict.get("suggestions"),
                bonus_coins=bonus_coins_val,
            )
            review_repo.create(new_review)

        return {
            "judge_review": judge_dict,
            "bonus_coins": bonus_coins_val,
            "current_status": "JUDGING_COMPLETED",
            "execution_logs": [
                f"[{timestamp}] Judge Node (Gemini): Evaluation completed | Score: {score_val}/10 | Bonus Coins: {bonus_coins_val}."
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
    """Reward Node: Calculates Reward = (2 * total_cost) + bonus_coins, updates order & directly credits user wallet balance."""
    logger.info("Entering reward_node for order_id=%s", state.get("order_id"))
    user_id = state["user_id"]
    order_id = state["order_id"]
    timestamp = datetime.now(timezone.utc).isoformat()

    wallet_service = WalletService(db)
    order_service = OrderService(db)
    order_repo = OrderRepository(db)
    review_repo = ReviewRepository(db)

    try:
        # 1. Fetch total_cost from order
        order = order_repo.get_by_id(order_id)
        total_cost = order.total_cost if order else Decimal("0.00")

        # 2. Fetch bonus_coins from review
        review_record = review_repo.get_by_order_id(order_id)
        bonus_coins = review_record.bonus_coins if review_record else Decimal("0.00")

        # 3. Calculate reward: Reward = (2 * total_cost) + bonus_coins
        total_reward = (Decimal("2.00") * total_cost) + bonus_coins

        # 4. Credit user wallet directly
        if total_reward > Decimal("0.00"):
            wallet_service.credit(
                user_id=user_id,
                amount=total_reward,
                description=f"Reward for Order #{order_id} (2 * {total_cost} + {bonus_coins} bonus)",
            )

        # 5. Update order record in DB & set COMPLETED status
        if order:
            order.reward_received = total_reward
            order_repo.update(order)

        order_service.update_status(order_id, "COMPLETED")
        final_balance = wallet_service.get_balance(user_id)

        logger.info(
            "Reward Node Completed | order_id=%s, total_cost=%s, bonus_coins=%s, total_reward=%s, final_balance=%s",
            order_id,
            total_cost,
            bonus_coins,
            total_reward,
            final_balance,
        )

        return {
            "bonus_coins": total_reward,
            "wallet_balance": final_balance,
            "current_status": "COMPLETED",
            "execution_logs": [
                f"[{timestamp}] Reward Node: Reward calculated ({total_reward} coins). Credited to wallet balance."
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
    """Persistence Node: Saves execution logs snapshot into workflow_executions table."""
    logger.info("Entering persistence_node for order_id=%s", state.get("order_id"))
    order_id = state["order_id"]
    user_id = state["user_id"]
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        from app.repositories.workflow_execution_repo import WorkflowExecutionRepository
        wf_repo = WorkflowExecutionRepository(db)

        wf_repo.record_execution(
            order_id=order_id,
            user_id=user_id,
            workflow_status=state.get("current_status", "COMPLETED"),
            execution_logs=state.get("execution_logs", []),
            error_logs=state.get("errors", []),
            graph_state_snapshot=state,
            final_wallet_balance=state.get("wallet_balance"),
            bonus_coins=state.get("bonus_coins"),
        )
        return {
            "execution_logs": [f"[{timestamp}] Persistence Node: Saved workflow execution record."],
        }
    except Exception as exc:
        logger.error("Persistence node failure: %s", exc)
        return {
            "errors": [f"Persistence node error: {exc}"],
        }


def fail_order_node(state: GraphState, db: Session) -> Dict[str, Any]:
    """Fail Order Node: Marks order status as FAILED and logs failure details."""
    logger.info("Entering fail_order_node for order_id=%s", state.get("order_id"))
    order_id = state.get("order_id")
    timestamp = datetime.now(timezone.utc).isoformat()

    try:
        if order_id:
            order_service = OrderService(db)
            order_service.update_status(order_id, "FAILED")
        return {
            "current_status": "FAILED",
            "execution_logs": [f"[{timestamp}] Fail Order Node: Workflow terminated with status FAILED."],
        }
    except Exception as exc:
        logger.error("Fail order node error: %s", exc)
        return {
            "current_status": "FAILED",
            "errors": [f"Fail order node error: {exc}"],
        }

