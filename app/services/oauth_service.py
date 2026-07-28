from app.config import settings as app_settings
from app.clients.supla_client import SuplaClient
from app.security.oauth_state import oauth_state
from app.stores.settings_store import SettingsStore
from app.models.oauth import OAuthToken
from collections.abc import Callable
from typing import TypeVar

from app.exceptions.supla import UnauthorizedError


T = TypeVar("T")


class OAuthService:
    """Business logic for the SUPLA OAuth flow."""

    def __init__(
        self,
        store: SettingsStore | None = None,
    ) -> None:
        self._settings_store = (
            store if store is not None else SettingsStore()
        )

    def begin_authorization(self) -> str:
        """Build the SUPLA OAuth authorization URL."""

        settings = self._settings_store.load()

        state = oauth_state.generate()

        client = SuplaClient(
            server=settings.supla.server,
        )

        return client.build_authorize_url(
            state=state,
        )

    def exchange_code(
        self,
        code: str,
    ) -> OAuthToken:
        """Exchange an authorization code for OAuth tokens."""

        settings = self._settings_store.load()

        client = SuplaClient(
            server=settings.supla.server,
        )

        return client.exchange_code(
            code=code,
            client_id=app_settings.supla_client_id,
            client_secret=app_settings.supla_client_secret,
            redirect_uri=app_settings.supla_redirect_uri,
        )

    def complete_authorization(
        self,
        code: str,
        state: str,
    ) -> None:
        """Complete the OAuth authorization flow."""

        oauth_state.validate(state)

        settings = self._settings_store.load()

        client = SuplaClient(
            server=settings.supla.server,
        )

        token = client.exchange_code(
            code=code,
            client_id=app_settings.supla_client_id,
            client_secret=app_settings.supla_client_secret,
            redirect_uri=app_settings.supla_redirect_uri,
        )

        settings.supla.access_token = token.access_token
        settings.supla.refresh_token = token.refresh_token

        self._settings_store.save(settings)

    def refresh_access_token(self) -> OAuthToken:
        settings = self._settings_store.load()

        if not settings.supla.refresh_token:
            raise ValueError("Refresh token is missing.")

        client = SuplaClient(
            server=settings.supla.server,
        )

        token = client.refresh_token(
            refresh_token=settings.supla.refresh_token,
            client_id=app_settings.supla_client_id,
            client_secret=app_settings.supla_client_secret,
        )

        settings.supla.access_token = token.access_token
        settings.supla.refresh_token = token.refresh_token

        self._settings_store.save(settings)

        return token

    def get_access_token(self) -> str:
        settings = self._settings_store.load()

        if not settings.supla.access_token:
            raise ValueError("Access token is missing.")

        return settings.supla.access_token

    def execute_with_token_refresh(
        self,
        operation: Callable[..., T],
        *args,
        **kwargs,
    ) -> T:
        """Execute a SUPLA API operation with automatic OAuth token refresh."""

        access_token = self.get_access_token()

        try:
            return operation(access_token, *args, **kwargs)

        except UnauthorizedError:
            token = self.refresh_access_token()

            return operation(token.access_token, *args, **kwargs)
