import json
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.session import SessionLocal
from app.models.order import Order
from app.models.recipe import Recipe
from app.models.review import Review
from app.models.wallet import Wallet
from app.models.workflow_execution import WorkflowExecution
from app.models.shopping import ShoppingHistory


def pretty(data):
    return json.dumps(data, indent=2, default=str)


def main():
    db = SessionLocal()

    print("==================================================")
    print("1. RECIPE API OUTPUT: GET /api/recipes/Tea")
    print("==================================================")
    recipe = db.query(Recipe).filter(Recipe.dish_name == "Tea").first()
    if recipe:
        print(pretty({
            "dish_name": recipe.dish_name,
            "recipe_json": recipe.recipe_json,
            "ingredients_json": recipe.ingredients_json,
            "estimated_cooking_time": recipe.estimated_cooking_time,
        }))

    print("\n==================================================")
    print("2. ORDER DETAILS API OUTPUT: GET /api/orders/{order_id} (Latest Tea Order)")
    print("==================================================")
    tea_order = db.query(Order).filter(Order.dish_name == "Tea").order_by(Order.created_at.desc()).first()
    if tea_order:
        shopping = db.query(ShoppingHistory).filter(ShoppingHistory.order_id == tea_order.id).all()
        review = db.query(Review).filter(Review.order_id == tea_order.id).first()

        shopping_list = [
            {"ingredient_name": s.ingredient_name, "quantity": str(s.quantity), "price": float(s.price)}
            for s in shopping
        ]

        review_data = {
            "score": float(review.score) if review and review.score is not None else 0.0,
            "review": review.review if review else None,
            "suggestions": review.suggestions if review else None,
            "bonus_coins": float(review.bonus_coins) if review and review.bonus_coins is not None else 0.0,
        } if review else None

        print(pretty({
            "id": tea_order.id,
            "user_id": tea_order.user_id,
            "dish_name": tea_order.dish_name,
            "status": tea_order.status,
            "total_cost": float(tea_order.total_cost) if tea_order.total_cost else 0.0,
            "reward_received": float(tea_order.reward_received) if tea_order.reward_received else 0.0,
            "shopping_summary": shopping_list,
            "judge_review": review_data,
            "created_at": tea_order.created_at,
        }))

    print("\n==================================================")
    print("3. REVIEW API OUTPUT: GET /api/reviews/Tea")
    print("==================================================")
    reviews = db.query(Review).join(Order).filter(Order.dish_name == "Tea").order_by(Review.created_at.desc()).all()
    print(pretty([
        {
            "id": r.id,
            "order_id": r.order_id,
            "score": float(r.score) if r.score is not None else 0.0,
            "review": r.review,
            "suggestions": r.suggestions,
            "bonus_coins": float(r.bonus_coins) if r.bonus_coins is not None else 0.0,
            "created_at": r.created_at
        } for r in reviews
    ]))

    print("\n==================================================")
    print("4. WALLET API OUTPUT: GET /api/wallet")
    print("==================================================")
    if tea_order:
        wallet = db.query(Wallet).filter(Wallet.user_id == tea_order.user_id).first()
        if wallet:
            print(pretty({
                "id": wallet.id,
                "user_id": wallet.user_id,
                "balance": float(wallet.balance),
                "updated_at": wallet.updated_at,
            }))

    print("\n==================================================")
    print("5. WORKFLOW AUDIT API OUTPUT: GET /api/workflow/{execution_id}")
    print("==================================================")
    if tea_order:
        exec_record = db.query(WorkflowExecution).filter(WorkflowExecution.order_id == tea_order.id).first()
        if exec_record:
            def safe_parse(val):
                if isinstance(val, (dict, list)):
                    return val
                if isinstance(val, str):
                    try:
                        return json.loads(val)
                    except Exception:
                        return val
                return val

            print(pretty({
                "id": exec_record.id,
                "order_id": exec_record.order_id,
                "user_id": exec_record.user_id,
                "workflow_status": exec_record.workflow_status,
                "execution_logs": safe_parse(exec_record.execution_logs),
                "error_logs": safe_parse(exec_record.error_logs),
                "graph_state_snapshot": safe_parse(exec_record.graph_state_snapshot),
            }))

    db.close()


if __name__ == "__main__":
    main()
