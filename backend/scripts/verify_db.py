"""Verify MySQL connectivity using backend settings."""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database.connection import engine


def main() -> None:
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"[SUCCESS] MySQL connection successful: SELECT 1 => {result.scalar()}")
    except Exception as exc:
        print(f"[FAILED] MySQL connection failed: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
