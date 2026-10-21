import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import settings as app_settings
from app.routers.web import setup as web_setup
from app.services.setup_service import SetupService
from app.stores.settings_store import SettingsStore


class SetupWebOAuthTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.store = SettingsStore(
            path=str(
                Path(self.temp_dir.name) / "config.json"
            )
        )

        self.service = SetupService(store=self.store)

        config = self.store.load()
        config.supla.server = "https://supla.example.com"
        config.supla.access_token = "existing-access"
        config.supla.refresh_token = "existing-refresh"
        self.store.save(config)

        self.app = FastAPI()
        self.app.include_router(web_setup.router)

        for target, attribute, value in (
            (
                web_setup,
                "setup_service",
                self.service,
            ),
            (
                app_settings,
                "supla_client_id",
                "legacy-id",
            ),
            (
                app_settings,
                "supla_client_secret",
                "legacy-secret",
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

        self.client = TestClient(
            self.app,
            base_url="https://testserver",
        )
        self.addCleanup(self.client.close)

    def submit(
        self,
        *,
        server="https://supla.example.com",
        client_id="legacy-id",
        client_secret="",
    ):
        return self.client.post(
            "/setup",
            data={
                "server": server,
                "client_id": client_id,
                "client_secret": client_secret,
                "csrf_token": "test",
            },
            follow_redirects=False,
        )

    def test_secret_is_not_displayed(self):
        response = self.client.get("/setup")

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            'name="client_id"',
            response.text,
        )
        self.assertIn(
            'name="client_secret"',
            response.text,
        )

        self.assertNotIn(
            "legacy-secret",
            response.text,
        )

    def test_legacy_credentials_preserve_connection(self):
        response = self.submit()

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["location"],
            "/dashboard",
        )

        config = self.store.load()

        self.assertEqual(
            config.supla.access_token,
            "existing-access",
        )
        self.assertEqual(
            config.supla.refresh_token,
            "existing-refresh",
        )

    def test_saved_secret_can_be_preserved(self):
        config = self.store.load()
        config.supla.client_id = "saved-id"
        config.supla.client_secret = "saved-secret"
        self.store.save(config)

        response = self.submit(
            client_id="saved-id",
        )

        self.assertEqual(response.status_code, 303)

        config = self.store.load()

        self.assertEqual(
            config.supla.client_secret,
            "saved-secret",
        )
        self.assertEqual(
            config.supla.access_token,
            "existing-access",
        )

    def test_new_id_requires_new_secret(self):
        response = self.submit(
            client_id="new-id",
        )

        self.assertEqual(response.status_code, 400)

        config = self.store.load()

        self.assertIsNone(config.supla.client_id)
        self.assertIsNone(config.supla.client_secret)

        self.assertEqual(
            config.supla.access_token,
            "existing-access",
        )

    def test_new_credentials_require_reauthorization(self):
        response = self.submit(
            client_id="new-id",
            client_secret="new-secret",
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["location"],
            "/oauth/login",
        )

        config = self.store.load()

        self.assertEqual(
            config.supla.client_id,
            "new-id",
        )
        self.assertEqual(
            config.supla.client_secret,
            "new-secret",
        )
        self.assertIsNone(config.supla.access_token)
        self.assertIsNone(config.supla.refresh_token)

    def test_server_change_requires_reauthorization(self):
        response = self.submit(
            server="https://another.supla.example.com",
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["location"],
            "/oauth/login",
        )

        config = self.store.load()

        self.assertIsNone(config.supla.access_token)
        self.assertIsNone(config.supla.refresh_token)

    def test_invalid_server_does_not_save_or_echo_secret(self):
        response = self.submit(
            server="invalid-url",
            client_id="new-id",
            client_secret="new-secret",
        )

        self.assertEqual(response.status_code, 400)

        self.assertNotIn(
            "new-secret",
            response.text,
        )

        config = self.store.load()

        self.assertEqual(
            config.supla.server,
            "https://supla.example.com",
        )
        self.assertIsNone(config.supla.client_id)

        self.assertEqual(
            config.supla.access_token,
            "existing-access",
        )


if __name__ == "__main__":
    unittest.main()
