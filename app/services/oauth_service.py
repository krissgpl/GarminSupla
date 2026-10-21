
from collections.abc import Callable
from typing import TypeVar

from app.clients.supla_client import SuplaClient
from app.config import settings as app_settings
from app.exceptions.supla import UnauthorizedError
from app.models.oauth import OAuthToken
from app.models.settings import Settings
from app.stores.settings_store import SettingsStore


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

    @staticmethod
    def _client_credentials(
        settings: Settings,
    ) -> tuple[str, str]:
        """Resolve saved credentials or legacy environment settings."""

        client_id = settings.supla.client_id
        client_secret = settings.supla.client_secret

        if client_id and client_secret:
            return client_id, client_secret

        if client_id or client_secret:
            raise ValueError(
                "Incomplete SUPLA OAuth client credentials."
            )

        return (
            app_settings.supla_client_id,
            app_settings.supla_client_secret,
        )

    def begin_authorization(
        self,
        state: str,
    ) -> str:
        """Build the SUPLA OAuth authorization URL."""

        settings = self._settings_store.load()

        client_id, _ = self._client_credentials(
            settings
        )

        client = SuplaClient(
            server=settings.supla.server,
        )

        return client.build_authorize_url(
            state=state,
            client_id=client_id,
        )

    def complete_authorization(
        self,
        code: str,
    ) -> None:
        """Complete the OAuth authorization flow."""

        settings = self._settings_store.load()

        client_id, client_secret = (
            self._client_credentials(settings)
        )

        client = SuplaClient(
            server=settings.supla.server,
        )

        token = client.exchange_code(
            code=code,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=app_settings.supla_redirect_uri,
        )

        settings.supla.access_token = token.access_token
        settings.supla.refresh_token = token.refresh_token

        self._settings_store.save(settings)

    def refresh_access_token(self) -> OAuthToken:
        settings = self._settings_store.load()

        if not settings.supla.refresh_token:
            raise ValueError("Refresh token is missing.")

        client_id, client_secret = (
            self._client_credentials(settings)
        )

        client = SuplaClient(
            server=settings.supla.server,
        )

        token = client.refresh_token(
            refresh_token=settings.supla.refresh_token,
            client_id=client_id,
            client_secret=client_secret,
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
        access_token = self.get_access_token()

        try:
            return operation(access_token, *args, **kwargs)

        except UnauthorizedError:
            token = self.refresh_access_token()

            return operation(token.access_token, *args, **kwargs)
