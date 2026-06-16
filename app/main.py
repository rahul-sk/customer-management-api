from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.customers import router as customers_router
from app.core.config import get_settings
from app.core.database import create_database_tables
from app.models import customer as customer_model

_ = customer_model


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    await create_database_tables()
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(customers_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
