from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.routers import gate, health, setup

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

templates = Jinja2Templates(directory="templates")

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
