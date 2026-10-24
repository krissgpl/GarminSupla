import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from pydantic import HttpUrl, ValidationError

from app.clients.supla_client import SuplaClient
from app.config import settings as app_settings
from app.models.oauth import OAuthToken
from app.models.settings import Settings
from app.services.oauth_service import OAuthService
from app.stores.settings_store import SettingsStore


LEGACY_URI = "https://legacy.example.com/oauth/callback"
SAVED_URI = "https://garmin.example.com/oauth/callback"


class OAuthRedirectUriTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.store = SettingsStore(
            path=str(
                Path(self.temp_dir.name) / "config.json"
            )
        )

        config = self.store.load()
        config.supla.client_id = "test-client-id"
        config.supla.client_secret = "test-client-secret"
        self.store.save(config)

        self.service = OAuthService(
            store=self.store
        )

        patcher = patch.object(
            app_settings,
            "supla_redirect_uri",
            LEGACY_URI,
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def _save_callback(self, uri):
        config = self.store.load()
        config.supla.redirect_uri = HttpUrl(uri)
        self.store.save(config)

    def _assert_authorization_callback(self, expected):
        url = self.service.begin_authorization(
            state="test-state"
        )

        params = parse_qs(
            urlsplit(url).query
        )

        self.assertEqual(
            params["redirect_uri"],
            [expected],
        )

        self.assertEqual(
            params["client_id"],
            ["test-client-id"],
        )

    def _assert_token_exchange_callback(self, expected):
        token = OAuthToken(
            access_token="test-access",
            refresh_token="test-refresh",
            token_type="Bearer",
            expires_in=3600,
        )

        with patch.object(
            SuplaClient,
            "exchange_code",
            return_value=token,
        ) as exchange:
            self.service.complete_authorization(
                code="test-code"
            )

        self.assertEqual(
            exchange.call_args.kwargs["redirect_uri"],
            expected,
        )

    def test_legacy_callback_from_environment(self):
        self._assert_authorization_callback(
            LEGACY_URI
        )

        self._assert_token_exchange_callback(
            LEGACY_URI
        )

    def test_saved_callback_overrides_environment(self):
        self._save_callback(SAVED_URI)

        self._assert_authorization_callback(
            SAVED_URI
        )

        self._assert_token_exchange_callback(
            SAVED_URI
        )

    def test_saved_callback_survives_reload(self):
        self._save_callback(SAVED_URI)

        restored = self.store.load()

        self.assertEqual(
            str(restored.supla.redirect_uri),
            SAVED_URI,
        )

    def test_invalid_callbacks_are_rejected(self):
        invalid_urls = (
            "http://garmin.example.com/oauth/callback",
            "https://garmin.example.com/other",
            "https://garmin.example.com/oauth/callback?x=1",
            "https://user:password@garmin.example.com/oauth/callback",
        )

        for uri in invalid_urls:
            with self.subTest(uri=uri):
                with self.assertRaises(ValidationError):
                    Settings.model_validate({
                        "supla": {
                            "redirect_uri": uri,
                        }
                    })


if __name__ == "__main__":
    unittest.main()
