from urllib.parse import urlencode

import httpx

from app.config import settings
from app.models.oauth import OAuthToken
from app.exceptions import (
    ApiError,
    RefreshTokenError,
    TokenExchangeError,
    UnauthorizedError,
)


class SuplaClient:
    """HTTP client for the SUPLA API."""

    def __init__(
        self,
        server: str,
        client: httpx.Client | None = None,
    ) -> None:
        self._server = server.rstrip("/")
        self._client = client or httpx.Client(timeout=10.0)

    def _url(self, path: str) -> str:
        """Build an absolute URL for the configured SUPLA server."""
        return f"{self._server.rstrip('/')}/{path.lstrip('/')}"

    def _raise_for_status(self, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                raise UnauthorizedError() from exc
            raise
    
    def build_authorize_url(
        self,
        state: str,
    ) -> str:
        """Build the SUPLA OAuth authorization URL."""

        params = {
            "client_id": settings.supla_client_id,
            "redirect_uri": settings.supla_redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": settings.supla_scope,
        }

        return f"{self._url('/oauth/v2/auth')}?{urlencode(params)}"

    def exchange_code(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> OAuthToken:
        """Exchange an OAuth authorization code for OAuth tokens."""

        try:
            response = self._client.post(
                self._url("/oauth/v2/token"),
                json={
                    "grant_type": "authorization_code",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "code": code,
                },
            )

            response.raise_for_status()

            return OAuthToken.model_validate(response.json())

        except httpx.HTTPStatusError as exc:

            if exc.response.status_code in (401, 403):
                raise UnauthorizedError(
                    "SUPLA API rejected the request."
                ) from exc

            raise TokenExchangeError(
                "Failed to exchange authorization code."
            ) from exc

        except httpx.RequestError as exc:

            raise ApiError(
                "Unable to communicate with the SUPLA API."
            ) from exc

    def refresh_token(
        self,
        refresh_token: str,
        client_id: str,
        client_secret: str,
    ) -> OAuthToken:

        try:
            response = self._client.post(
                self._url("/oauth/v2/token"),
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
            )

            response.raise_for_status()

            return OAuthToken.model_validate(response.json())

        except httpx.HTTPStatusError as exc:
            raise RefreshTokenError(
                "Failed to refresh access token."
            ) from exc

        except httpx.RequestError as exc:
            raise ApiError(
                "Unable to communicate with the SUPLA API."
            ) from exc

    def get_iodevices(
        self,
        access_token: str,
    ) -> list[dict]:
        response = self._client.get(
            self._url("/api/v2.4.0/iodevices"),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        self._raise_for_status(response)

        return response.json()

    def get_channels(
        self,
        access_token: str,
    ) -> list[dict]:
        response = self._client.get(
            self._url("/api/v2.4.0/channels"),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        self._raise_for_status(response)

        return response.json()
