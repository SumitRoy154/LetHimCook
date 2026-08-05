from fastapi import APIRouter

from app.core.config import get_settings
from app.database.connection import check_database_connection

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
def health_check() -> dict:
    db_connected = check_database_connection()

    groq_key_set = bool(settings.groq_api_key)
    anthropic_key_set = bool(settings.anthropic_api_key)
    google_key_set = bool(settings.google_api_key)

    return {
        "status": "healthy" if db_connected else "degraded",
        "app": settings.app_name,
        "version": settings.app_version,
        "database": {
            "engine": "mysql",
            "connected": db_connected,
        },
        "llm_providers": {
            "groq_planner": {"configured": groq_key_set, "provider": settings.planner_provider},
            "claude_cook": {"configured": anthropic_key_set, "provider": settings.cook_provider},
            "gemini_judge": {"configured": google_key_set, "provider": settings.judge_provider},
        },
    }
