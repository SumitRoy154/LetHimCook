from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, LogoutResponse, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserMeResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Register a new user account and automatically allocate a starting wallet with 1000 coins.",
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    auth_service = AuthService(db)
    created_user = auth_service.register(user_in)
    return UserResponse.model_validate(created_user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate a user using email or username along with their password, returning Access and Refresh JWT tokens.",
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    auth_service = AuthService(db)
    _, token_response = auth_service.authenticate(credentials)
    return token_response


@router.get(
    "/me",
    response_model=UserMeResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Current User Profile",
    description="Fetch current authenticated user details including user ID, username, email, and current wallet balance.",
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserMeResponse:
    balance = current_user.wallet.balance if current_user.wallet else 0.00
    return UserMeResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        wallet_balance=balance,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Access Token",
    description="Issue a new access token using a valid, unexpired refresh token.",
)
def refresh_token(
    body: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    auth_service = AuthService(db)
    return auth_service.refresh_access_token(body.refresh_token)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Logout endpoint structured for future token blacklisting/revocation integration.",
)
def logout(
    current_user: User = Depends(get_current_user),
) -> LogoutResponse:
    return LogoutResponse(message=f"User {current_user.username} successfully logged out")
