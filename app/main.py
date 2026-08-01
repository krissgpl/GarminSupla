from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.exception_handlers import register_exception_handlers

from app.config import settings

from app.routers.api import (
    gate,
    health,
    setup,
    supla,
)

from app.routers.web import (
    dashboard,
    oauth,
    setup as web_setup,
    select_gate,
    summary,
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

register_exception_handlers(app)

app.mount("/static", StaticFiles(directory="static"), name="static")

API_PREFIX = "/api/v1"

app.include_router(
    health.router,
    prefix=API_PREFIX,
)

app.include_router(
    gate.router,
    prefix=API_PREFIX,
)

app.include_router(
    supla.router,
    prefix=API_PREFIX,
)

app.include_router(
    setup.router,
    prefix=API_PREFIX,
)

app.include_router(
    web_setup.router,
)

app.include_router(
    oauth.router,
)

app.include_router(
    select_gate.router,
)

app.include_router(
    summary.router,
)

app.include_router(
    dashboard.router,
)
