from decimal import Decimal
from typing import Tuple

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.models.wallet import Wallet
from app.repositories.user_repo import UserRepository
from app.repositories.wallet_repo import WalletRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.wallet_repo = WalletRepository(db)

    def register(self, user_in: UserCreate) -> User:
        """Register a new user and automatically allocate a starting wallet with 1000 coins."""
        # 1. Check duplicate username
        if self.user_repo.get_by_username(user_in.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already registered",
            )

        # 2. Check duplicate email
        if self.user_repo.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

        # 3. Create user entity
        hashed_pwd = hash_password(user_in.password)
        new_user = User(
            username=user_in.username,
            email=user_in.email.lower(),
            password_hash=hashed_pwd,
        )
        created_user = self.user_repo.create(new_user)

        # 4. Automatically create Wallet with 1000 starting coins
        new_wallet = Wallet(
            user_id=created_user.id,
            balance=Decimal("1000.00"),
        )
        self.wallet_repo.create(new_wallet)

        return created_user

    def authenticate(self, credentials: LoginRequest) -> Tuple[User, TokenResponse]:
        """Authenticate user by username or email and return issued JWT tokens."""
        identifier = credentials.identifier.strip()

        # Resolve user by email or username
        if "@" in identifier:
            user = self.user_repo.get_by_email(identifier.lower())
        else:
            user = self.user_repo.get_by_username(identifier)

        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
        return user, token_response

    def refresh_access_token(self, refresh_token_str: str) -> TokenResponse:
        """Issue a new access token using a valid refresh token."""
        payload = decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        user = self.user_repo.get_by_id(int(user_id_str))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User no longer exists",
            )

        new_access_token = create_access_token(subject=user.id)
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
        )
