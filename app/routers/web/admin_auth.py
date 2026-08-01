from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.admin_auth_service import AdminAuthService


router = APIRouter()

templates = Jinja2Templates(directory="templates")

admin_auth_service = AdminAuthService()

SESSION_COOKIE = "garminsupla_admin_session"


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

    session = admin_auth_service.create_session(admin)

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
        max_age=8 * 60 * 60,
        path="/",
    )

    return response


@router.post("/logout")
async def logout():
    """Destroy administrator session."""

    response = RedirectResponse(
        url="/login",
        status_code=303,
    )

    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/",
    )

    return response
