"""Script to recreate shopping_histories and user_inventories tables using ingredient_id PK."""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database.connection import engine

def main():
    print("[+] Re-creating tables with ingredient_id PK/FK...")
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        conn.execute(text("DROP TABLE IF EXISTS shopping_histories;"))
        conn.execute(text("DROP TABLE IF EXISTS user_inventories;"))
        
        conn.execute(text("""
            CREATE TABLE user_inventories (
                id INT NOT NULL AUTO_INCREMENT,
                user_id INT NOT NULL,
                ingredient_id INT NOT NULL,
                quantity NUMERIC(10,2) NOT NULL DEFAULT '0.00',
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                UNIQUE KEY uq_user_item (user_id, ingredient_id),
                KEY ix_user_inventories_user_id (user_id),
                KEY ix_user_inventories_ingredient_id (ingredient_id),
                CONSTRAINT fk_user_inv_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                CONSTRAINT fk_user_inv_ingredient FOREIGN KEY (ingredient_id) REFERENCES inventories(ingredient_id) ON DELETE CASCADE
            );
        """))

        conn.execute(text("""
            CREATE TABLE shopping_histories (
                id INT NOT NULL AUTO_INCREMENT,
                order_id INT NOT NULL,
                ingredient_id INT NOT NULL,
                ingredient_name VARCHAR(100) NOT NULL,
                quantity NUMERIC(10,2) NOT NULL,
                price NUMERIC(10,2) NOT NULL,
                purchased_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (id),
                KEY ix_shopping_histories_order_id (order_id),
                KEY ix_shopping_histories_ingredient_id (ingredient_id),
                CONSTRAINT fk_shopping_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                CONSTRAINT fk_shopping_ingredient FOREIGN KEY (ingredient_id) REFERENCES inventories(ingredient_id) ON DELETE CASCADE
            );
        """))
        
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        print("[SUCCESS] All tables successfully recreated in MySQL!")

if __name__ == "__main__":
    main()
