import os
import unittest

from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import httpx

from app.clients.supla_client import SuplaClient
from app.config import AppSettings
from app.config import settings as app_settings


EXPECTED_SCOPE = (
    "iodevices_r channels_r channels_ea "
    "scenes_r scenes_ea offline_access"
)


class SuplaScopeDefaultTests(unittest.TestCase):

    def test_fresh_installation_uses_default_scope(self):
        with patch.dict(os.environ, {}, clear=True):
            config = AppSettings(
                _env_file=None,
                admin_session_secret="test-session-secret",
            )

        self.assertEqual(
            config.supla_scope,
            EXPECTED_SCOPE,
        )

    def test_environment_scope_overrides_default(self):
        custom_scope = (
            "channels_r channels_ea offline_access"
        )

        with patch.dict(
            os.environ,
            {
                "ADMIN_SESSION_SECRET": "test-session-secret",
                "SUPLA_SCOPE": custom_scope,
            },
            clear=True,
        ):
            config = AppSettings(
                _env_file=None,
            )

        self.assertEqual(
            config.supla_scope,
            custom_scope,
        )

    def test_authorization_url_contains_default_scope(self):
        with (
            patch.object(
                app_settings,
                "supla_scope",
                EXPECTED_SCOPE,
            ),
            httpx.Client() as http_client,
        ):
            client = SuplaClient(
                server="https://supla.example.com",
                client=http_client,
            )

            url = client.build_authorize_url(
                state="test-state",
                client_id="test-client-id",
                redirect_uri=(
                    "https://garmin.example.com/oauth/callback"
                ),
            )

        parsed = urlsplit(url)
        params = parse_qs(parsed.query)

        self.assertEqual(
            params["scope"],
            [EXPECTED_SCOPE],
        )

        self.assertEqual(
            params["client_id"],
            ["test-client-id"],
        )

        self.assertEqual(
            params["state"],
            ["test-state"],
        )

        self.assertEqual(
            params["redirect_uri"],
            [
                "https://garmin.example.com/oauth/callback"
            ],
        )


if __name__ == "__main__":
    unittest.main()
