from pydantic import ValidationError

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import settings
from app.core.templates import templates
from app.core.ui_language import resolve_ui_language
from app.models.setup import SetupForm
from app.services.setup_service import SetupService
from app.api.admin_auth import verify_admin_csrf


router = APIRouter()

setup_service = SetupService()


@router.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request):
    current = setup_service.load_settings()

    language = resolve_ui_language(
        request,
        current.ui.language,
    )

    return templates.TemplateResponse(
        request=request,
        name="setup.html",
        context={
            "title": (
                "Konfiguracja"
                if language == "pl"
                else "Setup"
            ),
            "version": settings.app_version,
            "language": language,
            "step": 1,
            "steps": 2,
            "form": {
                "server": current.supla.server,
                "client_id": (
                    current.supla.client_id
                    or settings.supla_client_id
                    or ""
                ),
            },
            "redirect_uri": settings.supla_redirect_uri,
            "errors": {},
            "csrf_token": request.cookies.get(
                "garminsupla_csrf"
            ),
        },
    )


@router.post("/setup", response_class=HTMLResponse)
async def setup_submit(
    request: Request,
    server: str = Form(...),
    client_id: str = Form(""),
    client_secret: str = Form(""),
    csrf_token: str = Form(...),
):
    verify_admin_csrf(
        request,
        csrf_token,
    )

    current = setup_service.load_settings()

    language = resolve_ui_language(
        request,
        current.ui.language,
    )

    form_data = {
        "server": server,
        "client_id": client_id.strip(),
    }

    errors = {}

    try:
        form = SetupForm.model_validate(
            {"server": server}
        )

    except ValidationError:
        form = None

        errors["server"] = (
            "Wpisz prawidłowy adres URL serwera SUPLA."
            if language == "pl"
            else "Enter a valid SUPLA server URL."
        )

    if not client_id.strip():
        errors["client_id"] = (
            "Client ID jest wymagany."
            if language == "pl"
            else "Client ID is required."
        )

    if not errors and form is not None:
        try:
            saved_settings = setup_service.save_setup(
                form,
                client_id=client_id,
                client_secret=client_secret,
            )

        except ValueError:
            errors["client_secret"] = (
                "Podaj Client Secret, jeśli zmieniasz "
                "aplikację OAuth lub konfiguracja "
                "jest niekompletna."
                if language == "pl"
                else
                "Enter Client Secret when changing "
                "the OAuth application or completing "
                "an incomplete configuration."
            )

        else:
            if saved_settings.supla.access_token:
                return RedirectResponse(
                    url="/dashboard",
                    status_code=303,
                )

            return RedirectResponse(
                url="/oauth/login",
                status_code=303,
            )

    return templates.TemplateResponse(
        request=request,
        name="setup.html",
        status_code=400,
        context={
            "title": (
                "Konfiguracja"
                if language == "pl"
                else "Setup"
            ),
            "version": settings.app_version,
            "language": language,
            "step": 1,
            "steps": 2,
            "form": form_data,
            "redirect_uri": settings.supla_redirect_uri,
            "errors": errors,
            "csrf_token": csrf_token,
        },
    )
