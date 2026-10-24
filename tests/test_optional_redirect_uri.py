import os
import re
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import AppSettings
from app.config import settings as app_settings
from app.models.setup import SetupForm
from app.routers.web import setup as web_setup
from app.services.oauth_service import OAuthService
from app.services.setup_service import SetupService
from app.stores.settings_store import SettingsStore


CALLBACK = "https://garmin.example.com/oauth/callback"


class OptionalRedirectUriTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.store = SettingsStore(
            path=str(
                Path(self.temp_dir.name) / "config.json"
            )
        )

        config = self.store.load()
        config.supla.server = "https://supla.example.com"
        config.supla.client_id = "test-id"
        config.supla.client_secret = "test-secret"
        config.supla.access_token = "existing-access"
        config.supla.refresh_token = "existing-refresh"
        self.store.save(config)

        self.setup_service = SetupService(
            store=self.store
        )

        self.oauth_service = OAuthService(
            store=self.store
        )

        for target, attribute, value in (
            (
                app_settings,
                "supla_redirect_uri",
                None,
            ),
            (
                web_setup,
                "setup_service",
                self.setup_service,
            ),
        ):
            patcher = patch.object(
                target,
                attribute,
                value,
            )
            patcher.start()
            self.addCleanup(patcher.stop)

        csrf_patcher = patch.object(
            web_setup,
            "verify_admin_csrf",
        )
        csrf_patcher.start()
        self.addCleanup(csrf_patcher.stop)

        app = FastAPI()
        app.include_router(web_setup.router)

        self.client = TestClient(
            app,
            base_url="https://testserver",
        )
        self.addCleanup(self.client.close)

    def test_settings_start_without_callback(self):
        with patch.dict(
            os.environ,
            {},
            clear=True,
        ):
            fresh = AppSettings(
                _env_file=None,
                admin_session_secret="test-session-secret",
                supla_scope="test-scope",
            )

        self.assertIsNone(
            fresh.supla_redirect_uri
        )

    def test_wizard_displays_empty_callback(self):
        response = self.client.get("/setup")

        self.assertEqual(
            response.status_code,
            200,
        )

        field = re.search(
            r'<input\b(?=[^>]*name="redirect_uri")[^>]*>',
            response.text,
            re.DOTALL,
        )

        self.assertIsNotNone(field)
        self.assertIn(
            'value=""',
            field.group(),
        )

    def test_oauth_rejects_missing_callback(self):
        with self.assertRaisesRegex(
            ValueError,
            "redirect URI is not configured",
        ):
            self.oauth_service.begin_authorization(
                state="test-state"
            )

    def test_service_rejects_incomplete_setup(self):
        form = SetupForm(
            server="https://supla.example.com"
        )

        with self.assertRaisesRegex(
            ValueError,
            "redirect URI is required",
        ):
            self.setup_service.save_setup(
                form,
                client_id="test-id",
                client_secret="",
            )

        saved = self.store.load()

        self.assertIsNone(
            saved.supla.redirect_uri
        )
        self.assertEqual(
            saved.supla.access_token,
            "existing-access",
        )
        self.assertEqual(
            saved.supla.refresh_token,
            "existing-refresh",
        )

    def test_post_rejects_missing_callback(self):
        response = self.client.post(
            "/setup",
            data={
                "server": "https://supla.example.com",
                "client_id": "new-id",
                "client_secret": "new-secret",
                "redirect_uri": "",
                "csrf_token": "test",
            },
            follow_redirects=False,
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertNotIn(
            "new-secret",
            response.text,
        )

        saved = self.store.load()

        self.assertEqual(
            saved.supla.client_id,
            "test-id",
        )
        self.assertEqual(
            saved.supla.client_secret,
            "test-secret",
        )
        self.assertEqual(
            saved.supla.access_token,
            "existing-access",
        )
        self.assertIsNone(
            saved.supla.redirect_uri
        )

    def test_saved_callback_enables_oauth(self):
        response = self.client.post(
            "/setup",
            data={
                "server": "https://supla.example.com",
                "client_id": "test-id",
                "client_secret": "",
                "redirect_uri": CALLBACK,
                "csrf_token": "test",
            },
            follow_redirects=False,
        )

        self.assertEqual(
            response.status_code,
            303,
        )

        self.assertEqual(
            response.headers["location"],
            "/oauth/login",
        )

        saved = self.store.load()

        self.assertEqual(
            str(saved.supla.redirect_uri),
            CALLBACK,
        )

        self.assertIsNone(
            saved.supla.access_token
        )
        self.assertIsNone(
            saved.supla.refresh_token
        )

        authorization_url = (
            self.oauth_service.begin_authorization(
                state="test-state"
            )
        )

        params = parse_qs(
            urlsplit(authorization_url).query
        )

        self.assertEqual(
            params["redirect_uri"],
            [CALLBACK],
        )
        self.assertEqual(
            params["client_id"],
            ["test-id"],
        )


if __name__ == "__main__":
    unittest.main()
