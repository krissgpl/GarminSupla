from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.api.admin_auth import verify_admin_csrf
from app.config import settings
from app.core.ui_language import resolve_ui_language
from app.services.admin_auth_service import AdminAuthService
from app.services.setup_service import SetupService

router = APIRouter()

templates = Jinja2Templates(directory="templates")

admin_auth_service = AdminAuthService()
setup_service = SetupService()

SESSION_COOKIE = "garminsupla_admin_session"
CSRF_COOKIE = "garminsupla_csrf"
SESSION_MAX_AGE = 8 * 60 * 60


@router.get(
    "/login",
    response_class=HTMLResponse,
)
async def login_page(request: Request):
    """Display administrator login page."""

    current = setup_service.load_settings()

    language = resolve_ui_language(
        request,
        current.ui.language,
    )

    page_title = (
        "Logowanie"
        if language == "pl"
        else "Login"
    )

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "title": page_title,
            "version": settings.app_version,
            "language": language,
            "error": None,
        },
    )


@router.post(
    "/login",
    response_class=HTMLResponse,
)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Authenticate administrator."""

    admin = admin_auth_service.verify_credentials(
        username,
        password,
    )

    if admin is None:
        current = setup_service.load_settings()

        language = resolve_ui_language(
            request,
            current.ui.language,
        )

        page_title = (
            "Logowanie"
            if language == "pl"
            else "Login"
        )

        error = (
            "Nieprawidłowa nazwa użytkownika lub hasło."
            if language == "pl"
            else "Invalid username or password."
        )

        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "title": page_title,
                "version": settings.app_version,
                "language": language,
                "error": error,
            },
            status_code=401,
        )

    session = admin_auth_service.create_session(
        admin
    )

    csrf_token = admin_auth_service.create_csrf_token(
        session
    )

    response = RedirectResponse(
        url="/dashboard",
        status_code=303,
    )

    response.set_cookie(
        key=SESSION_COOKIE,
        value=session,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )

    response.set_cookie(
        key=CSRF_COOKIE,
        value=csrf_token,
        httponly=False,
        secure=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )

    return response


@router.post("/logout")
async def logout(
    request: Request,
    csrf_token: str = Form(...),
):
    """Destroy administrator session."""

    verify_admin_csrf(
        request,
        csrf_token,
    )

    response = RedirectResponse(
        url="/login",
        status_code=303,
    )

    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
    )

    response.delete_cookie(
        key=CSRF_COOKIE,
        path="/",
    )

    return response
