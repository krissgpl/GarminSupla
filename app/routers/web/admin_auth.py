from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.admin_auth_service import AdminAuthService
from app.api.admin_auth import verify_admin_csrf

router = APIRouter()

templates = Jinja2Templates(directory="templates")

admin_auth_service = AdminAuthService()

SESSION_COOKIE = "garminsupla_admin_session"
CSRF_COOKIE = "garminsupla_csrf"
SESSION_MAX_AGE = 8 * 60 * 60


@router.get(
    "/login",
    response_class=HTMLResponse,
)
async def login_page(request: Request):
    """Display administrator login page."""

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
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
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid username or password.",
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
