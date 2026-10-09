from fastapi import FastAPI

from app.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.routers.api import pairing, watch


watch_app = FastAPI(
    title=f"{settings.app_name} Watch API",
    version=settings.app_version,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

register_exception_handlers(watch_app)

API_PREFIX = "/api/v1"

watch_app.include_router(
    watch.router,
    prefix=API_PREFIX,
)

watch_app.include_router(
    pairing.router,
    prefix=API_PREFIX,
)
