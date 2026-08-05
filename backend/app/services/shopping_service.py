import logging
from decimal import Decimal
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.shopping import ShoppingHistory
from app.repositories.shopping_repo import ShoppingHistoryRepository
from app.services.inventory_service import InventoryService
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)

# List of zero-cost kitchen staples that are stocked at 0 cost
STAPLE_INGREDIENTS = {"water", "salt", "black pepper", "oil", "cooking oil", "butter"}


class ShoppingService:
    def __init__(self, db: Session):
        self.db = db
        self.inventory_service = InventoryService(db)
        self.wallet_service = WalletService(db)
        self.shopping_repo = ShoppingHistoryRepository(db)

    def calculate_missing_items(
        self,
        user_id: int,
        recipe_ingredients: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Compare user's current inventory stock against required ingredients and return missing items."""
        missing_items = []
        user_inventory = {
            item["ingredient_name"]: item["quantity"]
            for item in self.inventory_service.get_inventory(user_id)
        }

        for req in recipe_ingredients:
            name = str(req.get("name", "")).lower().strip()
            needed_qty = Decimal(str(req.get("quantity", 0)))
            unit = str(req.get("unit", "units"))

            # Force 0.00 price for kitchen staples
            is_staple = name in STAPLE_INGREDIENTS or req.get("price") == 0 or req.get("price") == "0.00"
            est_price = Decimal("0.00") if is_staple else Decimal(str(req.get("price", "15.00")))

            owned_qty = user_inventory.get(name, Decimal("0.00"))

            if owned_qty < needed_qty:
                deficit = needed_qty - owned_qty
                missing_items.append({
                    "name": name,
                    "quantity": deficit,
                    "unit": unit,
                    "price_per_unit": est_price,
                    "total_price": deficit * est_price,
                    "is_staple": is_staple,
                })

        return missing_items

    def calculate_cost(self, missing_items: List[Dict[str, Any]]) -> Decimal:
        """Calculate total purchase cost for missing items excluding zero-price staples."""
        total = Decimal("0.00")
        for item in missing_items:
            total += Decimal(str(item.get("total_price", 0)))
        return total

    def purchase_missing_items(
        self,
        user_id: int,
        order_id: int,
        recipe_ingredients: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Buy missing ingredients: debit wallet for paid items, add stock to user_inventories, and log history."""
        missing = self.calculate_missing_items(user_id, recipe_ingredients)

        if not missing:
            logger.info("All ingredients already owned | user_id=%s, order_id=%s", user_id, order_id)
            return {
                "user_id": user_id,
                "order_id": order_id,
                "total_cost": Decimal("0.00"),
                "purchased_items": [],
                "already_owned": True,
            }

        total_cost = self.calculate_cost(missing)

        # 1. Debit wallet if total_cost > 0
        if total_cost > Decimal("0.00"):
            self.wallet_service.debit(
                user_id=user_id,
                amount=total_cost,
                description=f"Shopping for order #{order_id}",
            )

        # 2. Add missing items to user_inventories stock & create ShoppingHistory entries
        purchased_history_items = []
        for item in missing:
            user_inv = self.inventory_service.add_item(
                user_id=user_id,
                ingredient_name=item["name"],
                quantity=item["quantity"],
                unit=item["unit"],
                purchase_price=item["price_per_unit"],
            )

            # Record in shopping history using exact ingredient_id
            sh_entry = ShoppingHistory(
                order_id=order_id,
                ingredient_id=user_inv.ingredient_id,
                ingredient_name=item["name"],
                quantity=item["quantity"],
                price=item["total_price"],
            )
            created_entry = self.shopping_repo.create(sh_entry)
            purchased_history_items.append(created_entry)

        logger.info(
            "Shopping purchase completed | user_id=%s, order_id=%s, total_cost=%s, items_stocked=%s",
            user_id,
            order_id,
            total_cost,
            len(purchased_history_items),
        )

        return {
            "user_id": user_id,
            "order_id": order_id,
            "total_cost": total_cost,
            "purchased_items": missing,
            "already_owned": False,
        }
