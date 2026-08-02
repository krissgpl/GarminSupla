from fastapi import HTTPException, Request, status

from app.models.admin import AdminAccount
from app.services.admin_auth_service import AdminAuthService
from app.exceptions.admin import AdminAuthenticationRequired


SESSION_COOKIE = "garminsupla_admin_session"
CSRF_HEADER = "X-CSRF-Token"

admin_auth_service = AdminAuthService()


def get_current_admin(
    request: Request,
) -> AdminAccount | None:
    """Return the authenticated administrator or None."""

    session = request.cookies.get(
        SESSION_COOKIE
    )

    if not session:
        return None

    return admin_auth_service.verify_session(
        session
    )


def require_admin(
    request: Request,
) -> AdminAccount:
    """Require a valid administrator session."""

    admin = get_current_admin(request)

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Administrator authentication required.",
        )

    return admin

def require_admin_web(
    request: Request,
) -> AdminAccount:
    """Require administrator authentication for a web page."""

    admin = get_current_admin(request)

    if admin is None:
        raise AdminAuthenticationRequired()

    return admin

def require_admin_csrf(
    request: Request,
) -> AdminAccount:
    """Require administrator authentication and a valid CSRF token."""

    admin = require_admin(request)

    session = request.cookies.get(
        SESSION_COOKIE
    )

    csrf_token = request.headers.get(
        CSRF_HEADER
    )

    if (
        session is None
        or csrf_token is None
        or not admin_auth_service.verify_csrf_token(
            session,
            csrf_token,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token.",
        )

    return admin

def verify_admin_csrf(
    request: Request,
    csrf_token: str,
) -> None:
    """Verify a CSRF token submitted by an administrator."""

    session = request.cookies.get(
        SESSION_COOKIE
    )

    if (
        session is None
        or not admin_auth_service.verify_csrf_token(
            session,
            csrf_token,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid CSRF token.",
        )
