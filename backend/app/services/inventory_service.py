import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.exceptions.inventory import (
    IngredientNotFoundException,
    InsufficientIngredientException,
)
from app.models.inventory import Inventory, UserInventory
from app.repositories.inventory_repo import InventoryRepository, UserInventoryRepository

logger = logging.getLogger(__name__)


class InventoryService:
    def __init__(self, db: Session):
        self.db = db
        self.inventory_repo = InventoryRepository(db)
        self.user_inventory_repo = UserInventoryRepository(db)

    def get_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        """Return all inventory items owned by a user joined with item details."""
        user_items = self.user_inventory_repo.get_by_user_id(user_id)
        result = []
        for ui in user_items:
            if ui.item:
                result.append({
                    "id": ui.id,
                    "ingredient_id": ui.ingredient_id,
                    "ingredient_name": ui.item.ingredient_name,
                    "quantity": ui.quantity,
                    "unit": ui.item.unit,
                    "purchase_price": ui.item.purchase_price,
                })
        return result

    def get_or_create_global_item(
        self,
        ingredient_name: str,
        unit: str,
        purchase_price: Decimal = Decimal("0.00"),
    ) -> Inventory:
        """Get existing global catalog item or create it if not found."""
        normalized_name = ingredient_name.lower().strip()
        item = self.inventory_repo.get_by_name(normalized_name)
        if not item:
            item = Inventory(
                ingredient_name=normalized_name,
                unit=unit,
                purchase_price=purchase_price,
            )
            item = self.inventory_repo.create(item)
            logger.info("Global item catalog entry created | name=%s, price=%s", normalized_name, purchase_price)
        elif purchase_price > Decimal("0.00") and item.purchase_price == Decimal("0.00"):
            item.purchase_price = purchase_price
            item = self.inventory_repo.update(item)
        return item

    def add_item(
        self,
        user_id: int,
        ingredient_name: str,
        quantity: Decimal,
        unit: str,
        purchase_price: Decimal = Decimal("0.00"),
    ) -> UserInventory:
        """Add or update an ingredient stock in user's inventory."""
        if quantity <= Decimal("0.00"):
            raise ValueError("Quantity to add must be greater than zero.")

        global_item = self.get_or_create_global_item(ingredient_name, unit, purchase_price)
        existing_ui = self.user_inventory_repo.get_user_item(user_id, global_item.ingredient_id)

        if existing_ui:
            existing_ui.quantity += quantity
            updated_ui = self.user_inventory_repo.update(existing_ui)
            logger.info(
                "UserInventory updated | user_id=%s, item=%s, added=%s, total=%s",
                user_id,
                global_item.ingredient_name,
                quantity,
                updated_ui.quantity,
            )
            return updated_ui
        else:
            new_ui = UserInventory(
                user_id=user_id,
                ingredient_id=global_item.ingredient_id,
                quantity=quantity,
            )
            created_ui = self.user_inventory_repo.create(new_ui)
            logger.info(
                "UserInventory created | user_id=%s, item=%s, quantity=%s",
                user_id,
                global_item.ingredient_name,
                quantity,
            )
            return created_ui

    def remove_item(self, user_id: int, ingredient_name: str, quantity: Decimal) -> UserInventory:
        """Deduct ingredient quantity from user inventory."""
        if quantity <= Decimal("0.00"):
            raise ValueError("Quantity to remove must be greater than zero.")

        normalized_name = ingredient_name.lower().strip()
        ui = self.user_inventory_repo.get_user_ingredient_by_name(user_id, normalized_name)

        if not ui:
            raise IngredientNotFoundException(f"Ingredient '{ingredient_name}' not found in user inventory.")

        if ui.quantity < quantity:
            raise InsufficientIngredientException(
                f"Cannot remove {quantity} {ui.item.unit if ui.item else 'units'} of '{ingredient_name}'. Only {ui.quantity} available."
            )

        ui.quantity -= quantity
        updated_ui = self.user_inventory_repo.update(ui)
        logger.info(
            "UserInventory quantity reduced | user_id=%s, ingredient=%s, deducted=%s, remaining=%s",
            user_id,
            normalized_name,
            quantity,
            updated_ui.quantity,
        )
        return updated_ui

    def has_required_ingredients(self, user_id: int, required_items: List[Dict[str, Any]]) -> bool:
        """Check if user owns all required ingredients with sufficient quantities."""
        for req in required_items:
            name = str(req.get("name", "")).lower().strip()
            req_qty = Decimal(str(req.get("quantity", 0)))
            ui = self.user_inventory_repo.get_user_ingredient_by_name(user_id, name)
            if not ui or ui.quantity < req_qty:
                return False
        return True

    def consume(self, user_id: int, required_items: List[Dict[str, Any]]) -> List[UserInventory]:
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
