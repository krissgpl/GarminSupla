from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.setup_service import SetupService
from app.api.admin_auth import is_admin_authenticated

router = APIRouter()

templates = Jinja2Templates(directory="templates")

setup_service = SetupService()

@router.get("/")
async def root():

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

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

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):

    if not is_admin_authenticated(request):
        return RedirectResponse(
            url="/login",
            status_code=303,
        )


    status = setup_service.get_status()

    if not status.setup_completed:
        return RedirectResponse(
            url="/setup",
            status_code=303,
        )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
        },
    )
