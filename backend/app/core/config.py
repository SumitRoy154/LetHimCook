from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Let Him Cook!"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True
    api_prefix: str = "/api"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # MySQL Configuration
    database_url_env: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[int] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_name: Optional[str] = None

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "root123"
    mysql_database: str = "let_him_cook"

    # JWT Authentication
    jwt_secret_key: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: str = "http://localhost:3000"

    # LLM API Keys
    anthropic_api_key: str = ""
    google_api_key: str = ""
    groq_api_key: str = ""

    # AI Role Provider Mapping (anthropic | google | groq)
    planner_provider: str = "groq"
    cook_provider: str = "anthropic"
    judge_provider: str = "google"

    # Model Configurations
    planner_model: str = "gpt-4o"
    planner_temperature: float = 0.3
    planner_max_tokens: int = 1500
    planner_timeout: float = 30.0

    cook_model: str = "claude-3-5-sonnet-20241022"
    cook_temperature: float = 0.7
    cook_max_tokens: int = 3000
    cook_timeout: float = 60.0

    judge_model: str = "gemini-1.5-pro"
    judge_temperature: float = 0.2
    judge_max_tokens: int = 1500
    judge_timeout: float = 30.0

    # LangGraph Settings
    langgraph_debug: bool = True
    max_planner_retries: int = 3
    max_cook_retries: int = 2
    max_judge_retries: int = 2

    # Project Settings
    initial_wallet_coins: int = 1000
    default_currency: str = "Coins"
    log_level: str = "INFO"

    @property
    def effective_db_host(self) -> str:
        return self.db_host or self.mysql_host

    @property
    def effective_db_port(self) -> int:
        return self.db_port or self.mysql_port

    @property
    def effective_db_user(self) -> str:
        return self.db_user or self.mysql_user

    @property
    def effective_db_password(self) -> str:
        return self.db_password if self.db_password is not None else self.mysql_password

    @property
    def effective_db_name(self) -> str:
        return self.db_name or self.mysql_database

    @property
    def database_url(self) -> str:
        import os
        env_url = os.getenv("DATABASE_URL") or os.getenv("DATABASE_URL_ENV") or self.database_url_env
        if env_url:
            # Strip query params like ssl-mode=... or ssl_mode=... that PyMySQL connect() rejects directly
            if "?" in env_url:
                base_url, query = env_url.split("?", 1)
                params = [p for p in query.split("&") if not (p.startswith("ssl-mode") or p.startswith("ssl_mode") or p.startswith("ssl="))]
                env_url = f"{base_url}?{'&'.join(params)}" if params else base_url
            return env_url
        return (
            f"mysql+pymysql://{self.effective_db_user}:{self.effective_db_password}"
            f"@{self.effective_db_host}:{self.effective_db_port}/{self.effective_db_name}"
        )

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.cors_origins or self.cors_origins.strip() == "*":
            return ["*"]
        origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        if "*" not in origins:
            origins.append("*")
        return origins


@lru_cache
def get_settings() -> Settings:
    return Settings()
