from pydantic import BaseModel


class OAuthToken(BaseModel):
    """OAuth access token returned by the SUPLA authorization server."""

    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class OAuthError(BaseModel):
    """OAuth error response."""

    error: str
    error_description: str | None = None
