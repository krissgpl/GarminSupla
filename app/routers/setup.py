from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import settings
from app.core.templates import templates

router = APIRouter()

@router.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="setup.html",
        context={
            "title": "Setup",
            "version": settings.app_version,
        },
    )
