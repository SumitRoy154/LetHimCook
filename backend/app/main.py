from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.inventory import router as inventory_router
from app.api.routes.orders import router as orders_router
from app.api.routes.recipes import router as recipes_router
from app.api.routes.reviews import router as reviews_router
from app.api.routes.wallet import router as wallet_router
from app.api.routes.workflow import router as workflow_router
from app.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(orders_router, prefix=settings.api_prefix)
app.include_router(wallet_router, prefix=settings.api_prefix)
app.include_router(inventory_router, prefix=settings.api_prefix)
app.include_router(reviews_router, prefix=settings.api_prefix)
app.include_router(workflow_router, prefix=settings.api_prefix)
app.include_router(recipes_router, prefix=settings.api_prefix)


@app.get("/")
def root() -> dict:
    return {
        "message": "Let Him Cook! API",
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
        "auth": f"{settings.api_prefix}/auth",
    }
