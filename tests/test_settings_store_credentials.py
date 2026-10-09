import tempfile
import unittest

from pathlib import Path

from app.models.settings import (
    Settings,
    WatchDevice,
)
from app.stores.settings_store import SettingsStore


class SettingsStoreCredentialTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.addCleanup(
            self.temp_dir.cleanup
        )

        self.path = (
            Path(self.temp_dir.name)
            / "config.json"
        )

        self.first_store = SettingsStore(
            path=str(self.path)
        )

        self.second_store = SettingsStore(
            path=str(self.path)
        )

        settings = Settings()

        watch = WatchDevice(
            id="watch-1",
            name="Test Watch",
            token_hash="old-token-hash",
            credential_revision=1,
            created_at="2026-10-03T00:00:00+00:00",
        )

        settings.watches = [
            watch
        ]

        self.first_store.save(
            settings
        )

    def test_stale_save_is_rejected_after_watch_token_rotation(
        self,
    ):
        stale = self.second_store.load()

        current = self.first_store.load()

        current_watch = (
            current.watches[0]
        )

        current_watch.token_hash = (
            "new-token-hash"
        )

        current_watch.credential_revision = 2

        self.first_store.save(
            current
        )

        stale.ui.theme = "dark"

        with self.assertRaisesRegex(
            ValueError,
            "Stale configuration write",
        ):
            self.second_store.save(
                stale
            )

        saved = self.first_store.load()

        self.assertEqual(
            saved.ui.theme,
            "auto",
        )

        self.assertEqual(
            saved.watches[0].token_hash,
            "new-token-hash",
        )

        self.assertEqual(
            saved.watches[0].credential_revision,
            2,
        )

    def test_same_revision_token_change_is_rejected(
        self,
    ):
        current = self.first_store.load()

        current_watch = (
            current.watches[0]
        )

        current_watch.token_hash = (
            "unexpected-token-hash"
        )

        with self.assertRaisesRegex(
            ValueError,
            "Conflicting Garmin watch credentials",
        ):
            self.first_store.save(
                current
            )

        saved = self.first_store.load()

        self.assertEqual(
            saved.watches[0].token_hash,
            "old-token-hash",
        )

        self.assertEqual(
            saved.watches[0].credential_revision,
            1,
        )

    def test_stale_save_cannot_restore_deleted_watch(
        self,
    ):
        stale = self.second_store.load()

        current = self.first_store.load()

        current.watches = []

        self.first_store.save(
            current
        )

        stale.ui.theme = "dark"

        with self.assertRaisesRegex(
            ValueError,
            "Stale configuration write",
        ):
            self.second_store.save(
                stale
            )

        saved = self.first_store.load()

        self.assertEqual(
            saved.ui.theme,
            "auto",
        )

        self.assertEqual(
            saved.watches,
            [],
        )


if __name__ == "__main__":
    unittest.main()
