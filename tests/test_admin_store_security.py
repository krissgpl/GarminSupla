
import tempfile
import unittest

from pathlib import Path

from app.models.admin import AdminAccount
from app.stores.admin_store import AdminStore


class AdminStoreSecurityTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.addCleanup(
            self.temp_dir.cleanup
        )

        path = (
            Path(self.temp_dir.name)
            / "admin.json"
        )

        self.store = AdminStore(
            path=str(path)
        )

        self.admin = AdminAccount(
            username="test-admin",
            password_hash="test-only-password-hash",
            created_at="2026-09-27T00:00:00+00:00",
        )

        self.store.save(
            self.admin
        )

    def test_rejects_stale_security_settings(self):
        stale = self.store.load()

        secured = stale.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "test-encrypted-secret",
                "session_version": 1,
            }
        )

        self.store.save(
            secured
        )

        with self.assertRaises(ValueError):
            self.store.save(
                stale
            )

        current = self.store.load()

        self.assertTrue(
            current.totp_enabled
        )

        self.assertEqual(
            current.session_version,
            1,
        )

        self.assertEqual(
            current.totp_secret_encrypted,
            "test-encrypted-secret",
        )

    def test_rejects_stale_write_from_another_store(self):
        second_store = AdminStore(
            path=str(self.store.path)
        )

        stale = second_store.load()

        updated = self.store.load().model_copy(
            update={
                "session_version": 2,
            }
        )

        self.store.save(
            updated
        )

        with self.assertRaises(ValueError):
            second_store.save(
                stale
            )

        current = self.store.load()

        self.assertEqual(
            current.session_version,
            2,
        )

    def test_allows_increasing_session_version(self):
        for version in (1, 2, 3):
            admin = self.store.load()

            updated = admin.model_copy(
                update={
                    "session_version": version,
                }
            )

            self.store.save(
                updated
            )

            self.assertEqual(
                self.store.load().session_version,
                version,
            )


if __name__ == "__main__":
    unittest.main()
