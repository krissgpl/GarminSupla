from fastapi import HTTPException, Request, status

from app.models.admin import AdminAccount
from app.services.admin_auth_service import AdminAuthService
from app.exceptions.admin import AdminAuthenticationRequired


SESSION_COOKIE = "garminsupla_admin_session"

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
