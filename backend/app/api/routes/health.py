from fastapi import APIRouter

from app.core.config import get_settings
from app.database.connection import check_database_connection

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
def health_check() -> dict:
    db_connected = check_database_connection()

    return {
        "status": "healthy" if db_connected else "degraded",
        "app": settings.app_name,
        "version": settings.app_version,
        "database": {
            "engine": "mysql",
            "connected": db_connected,
        },
    }
