from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings as app_settings
from app.core.ui_language import resolve_ui_language
from app.services.setup_service import SetupService


router = APIRouter()

templates = Jinja2Templates(directory="templates")

setup_service = SetupService()


@router.get("/")
async def root():
    status = setup_service.get_status()

    if status.setup_completed:
        return RedirectResponse(
            url="/dashboard",
            status_code=303,
        )

    return RedirectResponse(
        url="/setup",
        status_code=303,
    )


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
async def dashboard(request: Request):
    status = setup_service.get_status()

    if not status.setup_completed:
        return RedirectResponse(
            url="/setup",
            status_code=303,
        )

    csrf_token = request.cookies.get(
        "garminsupla_csrf"
    )

    settings = setup_service.load_settings()

    language = resolve_ui_language(
        request,
        settings.ui.language,
    )

    page_title = (
        "Panel"
        if language == "pl"
        else "Dashboard"
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": page_title,
            "version": app_settings.app_version,
            "csrf_token": csrf_token,
            "language": language,
        },
    )
