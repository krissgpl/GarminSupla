from fastapi import FastAPI

from app.config import settings
from app.routers import health
from app.routers import gate

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(
    health.router,
    prefix="/api/v1",
)

app.include_router(
    gate.router,
    prefix="/api/v1",
)
