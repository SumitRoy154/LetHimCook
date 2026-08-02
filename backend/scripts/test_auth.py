import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.session import SessionLocal
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


def main():
    print("=== TESTING USER AUTHENTICATION & WALLET INITIALIZATION ===")
    db = SessionLocal()
    auth_service = AuthService(db)

    test_username = "test_auth_user"
    test_email = "test_auth@example.com"
    test_password = "password123"

    try:
        user = auth_service.register(
            UserCreate(username=test_username, email=test_email, password=test_password)
        )
        print(f"[SUCCESS] Registration successful: User #{user.id} ({user.username})")
        print(f"[SUCCESS] Wallet initialized: Balance = {user.wallet.balance} coins")
    except Exception as exc:
        print(f"[INFO] Registration notice: {exc}")
        user, tokens = auth_service.authenticate(
            LoginRequest(identifier=test_username, password=test_password)
        )
        if user:
            print(f"[SUCCESS] Login authentication successful: User #{user.id} ({user.username})")
            print(f"[SUCCESS] Issued JWT Access Token: {tokens.access_token[:25]}...")

    db.close()


if __name__ == "__main__":
    main()
