"""
Migration & Seed script:
1. Drop obsolete user_id and quantity columns from inventories table.
2. Truncate inventories table and reset auto-increment.
3. Seed 20 essential kitchen staple items into inventories catalog with purchase_price = 0.00.
"""

import sys
from pathlib import Path
from decimal import Decimal

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database.connection import engine
from app.database.session import SessionLocal
from app.models.inventory import Inventory

# 20 Essential Kitchen Staples (purchase_price = 0.00)
KITCHEN_STAPLES = [
    {"name": "water", "unit": "cup"},
    {"name": "salt", "unit": "tsp"},
    {"name": "black pepper", "unit": "tsp"},
    {"name": "cooking oil", "unit": "tbsp"},
    {"name": "butter", "unit": "tbsp"},
    {"name": "sugar", "unit": "tsp"},
    {"name": "turmeric powder", "unit": "tsp"},
    {"name": "red chili powder", "unit": "tsp"},
    {"name": "cumin seeds", "unit": "tsp"},
    {"name": "mustard seeds", "unit": "tsp"},
    {"name": "garlic paste", "unit": "tbsp"},
    {"name": "ginger paste", "unit": "tbsp"},
    {"name": "coriander leaves", "unit": "handful"},
    {"name": "curry leaves", "unit": "sprig"},
    {"name": "green chilies", "unit": "pieces"},
    {"name": "garam masala", "unit": "tsp"},
    {"name": "lemon juice", "unit": "tbsp"},
    {"name": "soy sauce", "unit": "tbsp"},
    {"name": "vinegar", "unit": "tbsp"},
    {"name": "cornstarch", "unit": "tbsp"},
]


def update_schema_and_seed():
    print("[+] Connecting to MySQL database...")
    with engine.begin() as conn:
        # Disable foreign key checks for clean structure updates
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        
        # 1. Truncate user_inventories and inventories
        print("[+] Truncating user_inventories and inventories tables...")
        conn.execute(text("TRUNCATE TABLE user_inventories;"))
        conn.execute(text("TRUNCATE TABLE inventories;"))
        
        # 2. Modify inventories table structure if user_id column still exists
        try:
            result = conn.execute(text("SHOW COLUMNS FROM inventories LIKE 'user_id';")).fetchone()
            if result:
                print("[+] Removing user_id & quantity columns from inventories table...")
                conn.execute(text("ALTER TABLE inventories DROP FOREIGN KEY inventories_ibfk_1;"))
            else:
                print("[+] user_id FK check passed.")
        except Exception as e:
            print(f"[!] FK drop notice: {e}")

        try:
            conn.execute(text("ALTER TABLE inventories DROP COLUMN user_id;"))
        except Exception:
            pass

        try:
            conn.execute(text("ALTER TABLE inventories DROP COLUMN quantity;"))
        except Exception:
            pass

        # Ensure ingredient_name is UNIQUE
        try:
            conn.execute(text("ALTER TABLE inventories ADD CONSTRAINT uq_ingredient_name UNIQUE (ingredient_name);"))
        except Exception:
            pass

        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

    # 3. Seed 20 Kitchen Staples into inventories table with price = 0.00
    print("[+] Seeding 20 kitchen staples with purchase_price = 0.00 into inventories table...")
    db = SessionLocal()
    try:
        for staple in KITCHEN_STAPLES:
            item = Inventory(
                ingredient_name=staple["name"],
                unit=staple["unit"],
                purchase_price=Decimal("0.00"),
            )
            db.add(item)
        db.commit()
        print("[SUCCESS] 20 Kitchen Staples successfully seeded into inventories table!")
    except Exception as exc:
        db.rollback()
        print(f"[ERROR] Failed to seed staples: {exc}")
    finally:
        db.close()

if __name__ == "__main__":
    update_schema_and_seed()
