from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.services.oauth_service import OAuthService

router = APIRouter(tags=["OAuth"])

oauth_service = OAuthService()


@router.get("/oauth/login")
def login() -> RedirectResponse:
    """Redirect the user to the SUPLA authorization page."""

    authorization_url = oauth_service.begin_authorization()

    return RedirectResponse(url=authorization_url)


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
