from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Username or Email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Valid long-lived refresh token")


class LogoutResponse(BaseModel):
    message: str = "Successfully logged out"
