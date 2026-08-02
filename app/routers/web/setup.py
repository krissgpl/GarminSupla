from pydantic import ValidationError

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import settings
from app.core.templates import templates
from app.models.setup import SetupForm
from app.services.setup_service import SetupService
from app.api.admin_auth import verify_admin_csrf

router = APIRouter()

setup_service = SetupService()


@router.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    current = setup_service.load_settings()

    csrf_token = request.cookies.get(
        "garminsupla_csrf"
    )

    return templates.TemplateResponse(
        request=request,
        name="setup.html",
        context={
            "title": "Setup",
            "version": settings.app_version,
            "step": 1,
            "steps": 4,
            "form": {
                "server": current.supla.server,
            },
            "errors": {},
            "csrf_token": csrf_token,
        },
    )


@router.post("/setup", response_class=HTMLResponse)
async def setup_submit(
    request: Request,
    server: str = Form(...),
    csrf_token: str = Form(...),
):

    verify_admin_csrf(
        request,
        csrf_token,
    )

    form_data = {
        "server": server,
    }

    try:
        form = SetupForm.model_validate(form_data)

    except ValidationError as exc:
        errors = {}

        for error in exc.errors():
            field = error["loc"][-1]
            errors[field] = error["msg"]

        return templates.TemplateResponse(
            request=request,
            name="setup.html",
            status_code=400,
            context={
                "title": "Setup",
                "version": settings.app_version,
                "step": 1,
                "steps": 4,
                "form": form_data,
                "errors": errors,
                "csrf_token": csrf_token,
            },
        )

    saved_settings = setup_service.save_server(form)

    if saved_settings.supla.access_token:
        return RedirectResponse(
            url="/select-gate",
            status_code=303,
        )

    return RedirectResponse(
        url="/oauth/login",
        status_code=303,
    )
