import logging
from decimal import Decimal
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.exceptions.inventory import (
    IngredientNotFoundException,
    InsufficientIngredientException,
)
from app.models.inventory import Inventory
from app.repositories.inventory_repo import InventoryRepository

logger = logging.getLogger(__name__)


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.inventory_repo = InventoryRepository(db)

    def get_inventory(self, user_id: int) -> List[Inventory]:
        """Return all inventory items owned by a user."""
        return self.inventory_repo.get_by_user_id(user_id)

    def ingredient_exists(self, user_id: int, name: str) -> bool:
        """Check if an ingredient exists in user's inventory with quantity > 0."""
        item = self.inventory_repo.get_user_ingredient(user_id, name.lower().strip())
        return item is not None and item.quantity > Decimal("0.00")

    def add_item(
        self,
        user_id: int,
        ingredient_name: str,
        quantity: Decimal,
        unit: str,
        purchase_price: Decimal = Decimal("0.00"),
    ) -> Inventory:
        """Add or update an ingredient in user's inventory."""
        if quantity <= Decimal("0.00"):
            raise ValueError("Quantity to add must be greater than zero.")

        normalized_name = ingredient_name.lower().strip()
        existing = self.inventory_repo.get_user_ingredient(user_id, normalized_name)

        if existing:
            existing.quantity += quantity
            existing.unit = unit
            if purchase_price > Decimal("0.00"):
                existing.purchase_price = purchase_price
            updated_item = self.inventory_repo.update(existing)
            logger.info(
                "Inventory updated | user_id=%s, ingredient=%s, added=%s, total=%s",
                user_id,
                normalized_name,
                quantity,
                updated_item.quantity,
            )
            return updated_item
        else:
            new_item = Inventory(
                user_id=user_id,
                ingredient_name=normalized_name,
                quantity=quantity,
                unit=unit,
                purchase_price=purchase_price,
            )
            created_item = self.inventory_repo.create(new_item)
            logger.info(
                "Inventory item created | user_id=%s, ingredient=%s, quantity=%s",
                user_id,
                normalized_name,
                quantity,
            )
            return created_item

    def remove_item(self, user_id: int, ingredient_name: str, quantity: Decimal) -> Inventory:
        """Deduct ingredient quantity from inventory. Prevents negative inventory stock."""
        if quantity <= Decimal("0.00"):
            raise ValueError("Quantity to remove must be greater than zero.")

        normalized_name = ingredient_name.lower().strip()
        item = self.inventory_repo.get_user_ingredient(user_id, normalized_name)

        if not item:
            raise IngredientNotFoundException(f"Ingredient '{ingredient_name}' not found in user inventory.")

        if item.quantity < quantity:
            raise InsufficientIngredientException(
                f"Cannot remove {quantity} {item.unit} of '{ingredient_name}'. Only {item.quantity} available."
            )

        item.quantity -= quantity
        updated_item = self.inventory_repo.update(item)
        logger.info(
            "Inventory quantity reduced | user_id=%s, ingredient=%s, deducted=%s, remaining=%s",
            user_id,
            normalized_name,
            quantity,
            updated_item.quantity,
        )
        return updated_item

    def has_required_ingredients(self, user_id: int, required_items: List[Dict[str, Any]]) -> bool:
        """Check if user owns all required ingredients with sufficient quantities."""
        for req in required_items:
            name = str(req.get("name", "")).lower().strip()
            req_qty = Decimal(str(req.get("quantity", 0)))
            item = self.inventory_repo.get_user_ingredient(user_id, name)
            if not item or item.quantity < req_qty:
                return False
        return True

    def consume(self, user_id: int, required_items: List[Dict[str, Any]]) -> List[Inventory]:
        """Consume recipe ingredients from user inventory after checking availability."""
        if not self.has_required_ingredients(user_id, required_items):
            raise InsufficientIngredientException("User does not have all required ingredients to consume.")

        consumed_items = []
        for req in required_items:
            name = str(req.get("name", "")).lower().strip()
            req_qty = Decimal(str(req.get("quantity", 0)))
            updated = self.remove_item(user_id, name, req_qty)
            consumed_items.append(updated)

        logger.info("Recipe ingredients consumed | user_id=%s, item_count=%s", user_id, len(consumed_items))
        return consumed_items
