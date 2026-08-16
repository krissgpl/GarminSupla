import secrets

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.api.admin_auth import require_admin_web
from app.models.admin import AdminAccount
from app.services.oauth_service import OAuthService


router = APIRouter(tags=["OAuth"])

oauth_service = OAuthService()

OAUTH_STATE_COOKIE = "garminsupla_oauth_state"
OAUTH_STATE_MAX_AGE = 10 * 60


@router.get("/oauth/login")
def login(
    admin: AdminAccount = Depends(require_admin_web),
) -> RedirectResponse:
    """Redirect the authenticated administrator to SUPLA authorization."""

    state = secrets.token_urlsafe(32)

    authorization_url = oauth_service.begin_authorization(
        state=state,
    )

    response = RedirectResponse(
        url=authorization_url,
    )

    response.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=state,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=OAUTH_STATE_MAX_AGE,
        path="/oauth",
    )

    return response


@router.get("/oauth/callback")
def callback(
    request: Request,
    code: str,
    state: str,
) -> RedirectResponse:
    """Handle the SUPLA OAuth callback."""

    expected_state = request.cookies.get(
        OAUTH_STATE_COOKIE
    )

    if (
        expected_state is None
        or not secrets.compare_digest(
            expected_state,
            state,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth state.",
        )

    oauth_service.complete_authorization(
        code=code,
    )

    response = RedirectResponse(
        url="/dashboard",
        status_code=303,
    )

    response.delete_cookie(
        key=OAUTH_STATE_COOKIE,
        path="/oauth",
    )

    return response
