import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import HttpUrl

from app.config import settings as app_settings
from app.routers.web import setup as web_setup
from app.services.setup_service import SetupService
from app.stores.settings_store import SettingsStore


LEGACY = "https://legacy.example.com/oauth/callback"
NEW = "https://garmin.example.com/oauth/callback"


class SetupRedirectUriWebTests(unittest.TestCase):

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
        config.supla.access_token = "old-access"
        config.supla.refresh_token = "old-refresh"
        self.store.save(config)

        service = SetupService(store=self.store)

        app = FastAPI()
        app.include_router(web_setup.router)

        for target, attribute, value in (
            (web_setup, "setup_service", service),
            (app_settings, "supla_client_id", "legacy-id"),
            (app_settings, "supla_client_secret", "legacy-secret"),
            (app_settings, "supla_redirect_uri", LEGACY),
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

        self.client = TestClient(
            app,
            base_url="https://testserver",
        )
        self.addCleanup(self.client.close)

    def submit(self, redirect_uri=LEGACY, include_uri=True):
        data = {
            "server": "https://supla.example.com",
            "client_id": "legacy-id",
            "client_secret": "",
            "csrf_token": "test",
        }

        if include_uri:
            data["redirect_uri"] = redirect_uri

        return self.client.post(
            "/setup",
            data=data,
            follow_redirects=False,
        )

    def test_get_displays_callback_field(self):
        self.client.cookies.set(
            "garminsupla_csrf",
            "test-csrf",
        )

        response = self.client.get("/setup")

        self.assertEqual(response.status_code, 200)
        self.assertIn('name="redirect_uri"', response.text)
        self.assertIn(
            'id="use-current-dashboard-callback"',
            response.text,
        )
        self.assertIn(
            'id="oauth-callback-preview"',
            response.text,
        )
        self.assertIn(
            'value="test-csrf"',
            response.text,
        )

    def test_saved_callback_is_displayed(self):
        config = self.store.load()
        config.supla.redirect_uri = HttpUrl(NEW)
        self.store.save(config)

        response = self.client.get("/setup")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f'value="{NEW}"',
            response.text,
        )

    def test_unchanged_callback_preserves_tokens(self):
        response = self.submit(LEGACY)

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["location"],
            "/dashboard",
        )

        config = self.store.load()

        self.assertEqual(
            str(config.supla.redirect_uri),
            LEGACY,
        )
        self.assertEqual(
            config.supla.access_token,
            "old-access",
        )
        self.assertEqual(
            config.supla.refresh_token,
            "old-refresh",
        )

    def test_changed_callback_invalidates_tokens(self):
        response = self.submit(NEW)

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["location"],
            "/oauth/login",
        )

        config = self.store.load()

        self.assertEqual(
            str(config.supla.redirect_uri),
            NEW,
        )
        self.assertIsNone(config.supla.access_token)
        self.assertIsNone(config.supla.refresh_token)

    def test_invalid_callback_does_not_change_settings(self):
        response = self.submit(
            "http://invalid.example.com/oauth/callback"
        )

        self.assertEqual(response.status_code, 400)

        config = self.store.load()

        self.assertIsNone(config.supla.redirect_uri)
        self.assertEqual(
            config.supla.access_token,
            "old-access",
        )

    def test_missing_callback_field_preserves_legacy(self):
        response = self.submit(include_uri=False)

        self.assertEqual(response.status_code, 303)

        config = self.store.load()

        self.assertIsNone(config.supla.redirect_uri)
        self.assertEqual(
            config.supla.access_token,
            "old-access",
        )


if __name__ == "__main__":
    unittest.main()
