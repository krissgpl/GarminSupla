import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from app.config import settings as app_settings
from app.services.setup_service import SetupService
from app.stores.settings_store import SettingsStore


class SetupOAuthCredentialsTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.store = SettingsStore(
            path=str(
                Path(self.temp_dir.name) / "config.json"
            )
        )

        self.service = SetupService(store=self.store)

        for name, value in (
            ("supla_client_id", "legacy-id"),
            ("supla_client_secret", "legacy-secret"),
        ):
            patcher = patch.object(
                app_settings,
                name,
                value,
            )
            patcher.start()
            self.addCleanup(patcher.stop)

    def _seed(
        self,
        client_id=None,
        client_secret=None,
    ):
        settings = self.store.load()

        settings.supla.client_id = client_id
        settings.supla.client_secret = client_secret
        settings.supla.access_token = "existing-access"
        settings.supla.refresh_token = "existing-refresh"

        self.store.save(settings)

    def _assert_tokens_preserved(self):
        settings = self.store.load()

        self.assertEqual(
            settings.supla.access_token,
            "existing-access",
        )
        self.assertEqual(
            settings.supla.refresh_token,
            "existing-refresh",
        )

    def test_legacy_migration_preserves_tokens(self):
        self._seed()

        self.service.save_oauth_credentials(
            client_id="legacy-id",
            client_secret="legacy-secret",
        )

        settings = self.store.load()

        self.assertEqual(
            settings.supla.client_id,
            "legacy-id",
        )
        self.assertEqual(
            settings.supla.client_secret,
            "legacy-secret",
        )

        self._assert_tokens_preserved()

    def test_changed_credentials_invalidate_tokens(self):
        for client_id, client_secret in (
            ("new-id", "legacy-secret"),
            ("legacy-id", "new-secret"),
        ):
            with self.subTest(
                client_id=client_id,
            ):
                self._seed()

                self.service.save_oauth_credentials(
                    client_id=client_id,
                    client_secret=client_secret,
                )

                settings = self.store.load()

                self.assertIsNone(
                    settings.supla.access_token
                )
                self.assertIsNone(
                    settings.supla.refresh_token
                )

    def test_unchanged_saved_credentials_preserve_tokens(self):
        self._seed(
            client_id="saved-id",
            client_secret="saved-secret",
        )

        self.service.save_oauth_credentials(
            client_id="saved-id",
            client_secret="saved-secret",
        )

        self._assert_tokens_preserved()

    def test_credentials_are_trimmed(self):
        self._seed()

        self.service.save_oauth_credentials(
            client_id="  legacy-id  ",
            client_secret="  legacy-secret  ",
        )

        settings = self.store.load()

        self.assertEqual(
            settings.supla.client_id,
            "legacy-id",
        )
        self.assertEqual(
            settings.supla.client_secret,
            "legacy-secret",
        )

        self._assert_tokens_preserved()

    def test_blank_credentials_are_rejected(self):
        self._seed()

        for client_id, client_secret in (
            ("", "new-secret"),
            ("new-id", ""),
            ("   ", "new-secret"),
        ):
            with self.subTest(client_id=client_id):
                with self.assertRaises(ValueError):
                    self.service.save_oauth_credentials(
                        client_id=client_id,
                        client_secret=client_secret,
                    )

                self._assert_tokens_preserved()

    def test_partial_stored_credentials_are_rejected(self):
        self._seed(
            client_id="partial-id",
            client_secret=None,
        )

        with self.assertRaisesRegex(
            ValueError,
            "Existing SUPLA OAuth credentials are incomplete",
        ):
            self.service.save_oauth_credentials(
                client_id="new-id",
                client_secret="new-secret",
            )

        settings = self.store.load()

        self.assertEqual(
            settings.supla.client_id,
            "partial-id",
        )
        self.assertIsNone(
            settings.supla.client_secret
        )

        self._assert_tokens_preserved()


if __name__ == "__main__":
    unittest.main()
