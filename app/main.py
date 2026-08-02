from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.exception_handlers import register_exception_handlers

from app.api.admin_auth import (
    require_admin,
    require_admin_web,
)

from app.config import settings

from app.routers.api import (
    pairing,
    setup,
    supla,
    watch,
)

from app.routers.web import (
    admin_auth,
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
    admin_auth.router,
)

app.include_router(
    supla.router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin)],
)

app.include_router(
    setup.router,
    prefix=API_PREFIX,
    dependencies=[Depends(require_admin)],
)

app.include_router(
    watch.router,
    prefix=API_PREFIX,
)

app.include_router(
    web_setup.router,
    dependencies=[Depends(require_admin_web)],
)

app.include_router(
    pairing.router,
    prefix=API_PREFIX,
)

app.include_router(
    oauth.router,
)

app.include_router(
    select_gate.router,
    dependencies=[Depends(require_admin_web)],
)

app.include_router(
    summary.router,
    dependencies=[Depends(require_admin_web)],
)

app.include_router(
    dashboard.router,
    dependencies=[Depends(require_admin_web)],
)
