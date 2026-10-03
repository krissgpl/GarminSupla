import tempfile
import unittest

from pathlib import Path

from app.models.admin import AdminAccount
from app.services.admin_auth_service import (
    AdminAuthService,
)
from app.stores.admin_store import AdminStore


class AdminTotpChallengeTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.addCleanup(
            self.temp_dir.cleanup
        )

        self.store = AdminStore(
            path=str(
                Path(self.temp_dir.name)
                / "admin.json"
            )
        )

        self.service = AdminAuthService()
        self.service._store = self.store

        self.admin = AdminAccount(
            username="test-admin",
            password_hash=(
                self.service._password_hash.hash(
                    "test-password-123"
                )
            ),
            created_at="2026-09-28T00:00:00+00:00",
            enabled=True,
            totp_enabled=True,
            totp_secret_encrypted=(
                "test-encrypted-secret"
            ),
            session_version=1,
        )

        self.store.save(
            self.admin
        )

    def test_creates_and_verifies_totp_challenge(self):
        challenge = (
            self.service.create_totp_challenge(
                self.admin
            )
        )

        verified = (
            self.service.verify_totp_challenge(
                challenge
            )
        )

        self.assertIsNotNone(
            verified
        )

        self.assertEqual(
            verified.username,
            "test-admin",
        )

        self.assertEqual(
            verified.session_version,
            1,
        )

    def test_rejects_modified_totp_challenge(self):
        challenge = (
            self.service.create_totp_challenge(
                self.admin
            )
        )

        modified = (
            challenge + ".invalid"
        )

        self.assertIsNone(
            self.service.verify_totp_challenge(
                modified
            )
        )

    def test_session_version_change_invalidates_challenge(self):
        challenge = (
            self.service.create_totp_challenge(
                self.admin
            )
        )

        updated = self.store.load().model_copy(
            update={
                "session_version": 2,
            }
        )

        self.store.save(
            updated
        )

        self.assertIsNone(
            self.service.verify_totp_challenge(
                challenge
            )
        )

    def test_disabling_totp_invalidates_challenge(self):
        challenge = (
            self.service.create_totp_challenge(
                self.admin
            )
        )

        updated = self.store.load().model_copy(
            update={
                "totp_enabled": False,
                "totp_secret_encrypted": None,
                "totp_last_used_counter": None,
                "session_version": 2,
            }
        )

        self.store.save(
            updated
        )

        self.assertIsNone(
            self.service.verify_totp_challenge(
                challenge
            )
        )

    def test_password_only_admin_cannot_create_challenge(self):
        admin = self.store.load().model_copy(
            update={
                "totp_enabled": False,
                "totp_secret_encrypted": None,
                "session_version": 2,
            }
        )

        self.store.save(
            admin
        )

        with self.assertRaises(ValueError):
            self.service.create_totp_challenge(
                admin
            )

    def test_disabled_admin_cannot_use_challenge(self):
        challenge = (
            self.service.create_totp_challenge(
                self.admin
            )
        )

        disabled = self.store.load().model_copy(
            update={
                "enabled": False,
            }
        )

        self.store.save(
            disabled
        )

        self.assertIsNone(
            self.service.verify_totp_challenge(
                challenge
            )
        )


if __name__ == "__main__":
    unittest.main()
