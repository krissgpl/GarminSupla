from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import gate, health, oauth, setup, supla, setup_api

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(
    health.router,
    prefix="/api/v1",
)

app.include_router(
    gate.router,
    prefix="/api/v1",
)

app.include_router(
    setup.router,
)

app.include_router(
    oauth.router,
)

app.include_router(
    supla.router,
)

app.include_router(
    setup_api.router,
)
