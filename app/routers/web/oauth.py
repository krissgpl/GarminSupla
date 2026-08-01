from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from app.api.admin_auth import require_admin
from app.models.admin import AdminAccount
from app.services.oauth_service import OAuthService


router = APIRouter(tags=["OAuth"])

oauth_service = OAuthService()


@router.get("/oauth/login")
def login(
    admin: AdminAccount = Depends(require_admin),
) -> RedirectResponse:
    """Redirect the authenticated administrator to SUPLA authorization."""

    authorization_url = oauth_service.begin_authorization()

    return RedirectResponse(
        url=authorization_url,
    )


@router.get("/oauth/callback")
def callback(
    code: str,
    state: str,
) -> RedirectResponse:
    """Handle the SUPLA OAuth callback."""

    oauth_service.complete_authorization(
        code=code,
        state=state,
    )

    return RedirectResponse(
        url="/setup",
        status_code=303,
    )
