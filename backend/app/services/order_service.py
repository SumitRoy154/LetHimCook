import logging
from typing import List, Set

from sqlalchemy.orm import Session

from app.exceptions.order import InvalidOrderStateException, OrderNotFoundException
from app.models.order import Order
from app.repositories.order_repo import OrderRepository

logger = logging.getLogger(__name__)

ALLOWED_STATUSES: Set[str] = {
    "PENDING",
    "SHOPPING",
    "COOKING",
    "JUDGING",
    "COMPLETED",
    "FAILED",
}

# State transition matrix
VALID_TRANSITIONS = {
    "PENDING": {"SHOPPING", "FAILED"},
    "SHOPPING": {"COOKING", "FAILED"},
    "COOKING": {"JUDGING", "FAILED"},
    "JUDGING": {"COMPLETED", "FAILED"},
    "COMPLETED": set(),
    "FAILED": set(),
}


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.order_repo = OrderRepository(db)

    def create_order(self, user_id: int, dish_name: str) -> Order:
        """Create a new food order in PENDING status."""
        new_order = Order(
            user_id=user_id,
            dish_name=dish_name.strip(),
            status="PENDING",
        )
        created_order = self.order_repo.create(new_order)
        logger.info("Order created | user_id=%s, dish_name='%s', order_id=%s", user_id, dish_name, created_order.id)
        return created_order

    def get_order_details(self, order_id: int) -> Order:
        """Fetch order details by order_id."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise OrderNotFoundException(f"Order #{order_id} not found.")
        return order

    def update_status(self, order_id: int, new_status: str) -> Order:
        """Update order status while enforcing strict state transition rules."""
        target_status = new_status.upper().strip()
        if target_status not in ALLOWED_STATUSES:
            raise InvalidOrderStateException(f"Unknown order status '{new_status}'. Allowed: {ALLOWED_STATUSES}")

        order = self.get_order_details(order_id)
        current_status = order.status.upper()

        if target_status not in VALID_TRANSITIONS.get(current_status, set()):
            logger.warning(
                "Invalid order transition blocked | order_id=%s, current=%s, target=%s",
                order_id,
                current_status,
                target_status,
            )
            raise InvalidOrderStateException(
                f"Cannot transition order #{order_id} from {current_status} to {target_status}."
            )

        order.status = target_status
        updated_order = self.order_repo.update(order)
        logger.info("Order status updated | order_id=%s, status=%s", order_id, target_status)
        return updated_order

    def get_order_history(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Order]:
        """Fetch order history for a user."""
        return self.order_repo.get_by_user_id(user_id, skip=skip, limit=limit)
