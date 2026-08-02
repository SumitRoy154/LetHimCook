import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.session import SessionLocal
from app.graph import build_cooking_graph
from app.repositories import UserRepository
from app.schemas.user import UserCreate
from app.services import AuthService, OrderService


def main():
    dish_name = sys.argv[1] if len(sys.argv) > 1 else "Egg Roll"
    db = SessionLocal()

    print(f"=== TESTING END-TO-END LANGGRAPH WORKFLOW FOR: '{dish_name}' ===")

    # 1. Register or fetch test user
    auth_service = AuthService(db)
    user_repo = UserRepository(db)
    user = user_repo.get_by_username("chef_master")

    if not user:
        user = auth_service.register(
            UserCreate(username="chef_master", email="chef@test.com", password="password123")
        )
        print(f"User Created: {user.username} (ID: {user.id}) | Balance: {user.wallet.balance} coins")
    else:
        print(f"User Loaded: {user.username} (ID: {user.id}) | Balance: {user.wallet.balance} coins")

    # 2. Create Food Order
    order_service = OrderService(db)
    order = order_service.create_order(user.id, dish_name)
    print(f"Order #{order.id} Created | Initial Status: {order.status}")

    # 3. Build & Run LangGraph Cooking Orchestrator
    graph = build_cooking_graph(db=db, mock=False)
    initial_state = {"user_id": user.id, "order_id": order.id}

    print("\n=== EXECUTING LANGGRAPH WORKFLOW ENGINE ===")
    final_state = graph.invoke(initial_state)

    print("\n=== WORKFLOW EXECUTION LOGS ===")
    for log in final_state.get("execution_logs", []):
        print(" ", log)

    print("\n=== SUMMARY ===")
    print("Final Status:", final_state.get("current_status"))
    print("Final Wallet Balance:", final_state.get("wallet_balance"))
    print("Bonus Coins Awarded:", final_state.get("bonus_coins"))
    print("Workflow Execution Audit Record ID:", final_state.get("workflow_execution_id"))

    db.close()


if __name__ == "__main__":
    main()
