import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from app.clients.supla_client import SuplaClient
from app.config import settings as app_settings
from app.models.oauth import OAuthToken
from app.services.oauth_service import OAuthService
from app.stores.settings_store import SettingsStore


class OAuthCredentialsTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.store = SettingsStore(
            path=str(
                Path(self.temp_dir.name) / "config.json"
            )
        )

        self.service = OAuthService(store=self.store)

        for field, value in (
            ("supla_client_id", "legacy-client-id"),
            ("supla_client_secret", "legacy-client-secret"),
        ):
            patcher = patch.object(
                app_settings,
                field,
                value,
            )
            patcher.start()
            self.addCleanup(patcher.stop)

    def _set_credentials(
        self,
        client_id,
        client_secret,
    ):
        settings = self.store.load()

        settings.supla.client_id = client_id
        settings.supla.client_secret = client_secret

        self.store.save(settings)

    def _assert_authorization_client_id(
        self,
        expected_client_id,
    ):
        url = self.service.begin_authorization(
            state="test-state"
        )

        params = parse_qs(urlsplit(url).query)

        self.assertEqual(
            params["client_id"],
            [expected_client_id],
        )

        self.assertEqual(
            params["state"],
            ["test-state"],
        )

        self.assertNotIn(
            "client_secret",
            params,
        )

    def _assert_token_credentials(
        self,
        expected_client_id,
        expected_client_secret,
    ):
        token = OAuthToken(
            access_token="access-token",
            refresh_token="refresh-token",
            token_type="Bearer",
            expires_in=3600,
        )

        with patch.object(
            SuplaClient,
            "exchange_code",
            return_value=token,
        ) as exchange:
            self.service.complete_authorization(
                "test-code"
            )

            self.assertEqual(
                exchange.call_args.kwargs["client_id"],
                expected_client_id,
            )

            self.assertEqual(
                exchange.call_args.kwargs["client_secret"],
                expected_client_secret,
            )

        saved = self.store.load()

        self.assertEqual(
            saved.supla.access_token,
            "access-token",
        )

        self.assertEqual(
            saved.supla.refresh_token,
            "refresh-token",
        )

        with patch.object(
            SuplaClient,
            "refresh_token",
            return_value=token,
        ) as refresh:
            self.service.refresh_access_token()

            self.assertEqual(
                refresh.call_args.kwargs["client_id"],
                expected_client_id,
            )

            self.assertEqual(
                refresh.call_args.kwargs["client_secret"],
                expected_client_secret,
            )

    def test_legacy_environment_credentials(self):
        self._assert_authorization_client_id(
            "legacy-client-id"
        )

        self._assert_token_credentials(
            "legacy-client-id",
            "legacy-client-secret",
        )

    def test_dashboard_credentials_override_environment(self):
        self._set_credentials(
            "dashboard-client-id",
            "dashboard-client-secret",
        )

        self._assert_authorization_client_id(
            "dashboard-client-id"
        )

        self._assert_token_credentials(
            "dashboard-client-id",
            "dashboard-client-secret",
        )

    def test_incomplete_credentials_are_rejected(self):
        for client_id, client_secret in (
            ("dashboard-client-id", None),
            (None, "dashboard-client-secret"),
        ):
            with self.subTest(
                client_id=client_id is not None,
                client_secret=client_secret is not None,
            ):
                self._set_credentials(
                    client_id,
                    client_secret,
                )

                with self.assertRaisesRegex(
                    ValueError,
                    "Incomplete SUPLA OAuth client credentials",
                ):
                    self.service.begin_authorization(
                        state="test-state"
                    )


if __name__ == "__main__":
    unittest.main()
