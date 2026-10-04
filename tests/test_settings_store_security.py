import stat
import tempfile
import unittest

from pathlib import Path

from app.models.settings import Settings
from app.stores.settings_store import SettingsStore


class SettingsStoreSecurityTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.addCleanup(
            self.temp_dir.cleanup
        )

        self.path = (
            Path(self.temp_dir.name)
            / "config.json"
        )

        self.store = SettingsStore(
            path=str(self.path)
        )

    def test_configuration_file_is_owner_only(self):
        settings = Settings()

        settings.supla.access_token = (
            "test-access-token"
        )

        settings.supla.refresh_token = (
            "test-refresh-token"
        )

        self.store.save(
            settings
        )

        mode = stat.S_IMODE(
            self.path.stat().st_mode
        )

        self.assertEqual(
            mode,
            0o600,
        )

    def test_rewrite_preserves_owner_only_permissions(self):
        settings = Settings()

        self.store.save(
            settings
        )

        self.path.chmod(
            0o644
        )

        settings.supla.access_token = (
            "updated-access-token"
        )

        self.store.save(
            settings
        )

        mode = stat.S_IMODE(
            self.path.stat().st_mode
        )

        self.assertEqual(
            mode,
            0o600,
        )


if __name__ == "__main__":
    unittest.main()
