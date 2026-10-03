import tempfile
import unittest

from pathlib import Path

from app.models.admin import AdminAccount
from app.services.admin_auth_service import (
    AdminAuthService,
)
from app.stores.admin_store import AdminStore


class AdminTotpDisableTests(unittest.TestCase):

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

        self.password = "test-password-123"

        self.admin = AdminAccount(
            username="test-admin",
            password_hash=(
                self.service._password_hash.hash(
                    self.password
                )
            ),
            created_at="2026-09-28T00:00:00+00:00",
            enabled=True,
            totp_enabled=True,
            totp_secret_encrypted=(
                "encrypted-test-secret"
            ),
            recovery_code_hashes=[
                "v1$recovery-hash-one",
                "v1$recovery-hash-two",
            ],
            totp_last_used_counter=123456,
            session_version=5,
        )

        self.store.save(
            self.admin
        )

    def test_disable_totp_clears_security_material(self):
        updated = self.service.disable_totp(
            self.admin,
            self.password,
        )

        self.assertFalse(
            updated.totp_enabled
        )

        self.assertIsNone(
            updated.totp_secret_encrypted
        )

        self.assertEqual(
            updated.recovery_code_hashes,
            [],
        )

        self.assertIsNone(
            updated.totp_last_used_counter
        )

        self.assertEqual(
            updated.session_version,
            6,
        )

        persisted = self.store.load()

        self.assertEqual(
            persisted,
            updated,
        )

    def test_disable_totp_invalidates_existing_session(self):
        session = (
            self.service._serializer.dumps(
                {
                    "username":
                        self.admin.username,
                    "session_version":
                        self.admin.session_version,
                    "totp_verified": True,
                }
            )
        )

        self.assertIsNotNone(
            self.service.verify_session(
                session
            )
        )

        self.service.disable_totp(
            self.admin,
            self.password,
        )

        self.assertIsNone(
            self.service.verify_session(
                session
            )
        )

    def test_disable_totp_invalidates_existing_challenge(self):
        challenge = (
            self.service.create_totp_challenge(
                self.admin
            )
        )

        self.assertIsNotNone(
            self.service.verify_totp_challenge(
                challenge
            )
        )

        self.service.disable_totp(
            self.admin,
            self.password,
        )

        self.assertIsNone(
            self.service.verify_totp_challenge(
                challenge
            )
        )

    def test_rejects_wrong_password(self):
        with self.assertRaises(ValueError):
            self.service.disable_totp(
                self.admin,
                "wrong-password",
            )

        current = self.store.load()

        self.assertTrue(
            current.totp_enabled
        )

        self.assertEqual(
            current.session_version,
            5,
        )

        self.assertEqual(
            len(current.recovery_code_hashes),
            2,
        )

    def test_rejects_stale_admin_snapshot(self):
        stale = self.store.load()

        current = stale.model_copy(
            update={
                "session_version": 6,
            }
        )

        self.store.save(
            current
        )

        with self.assertRaises(ValueError):
            self.service.disable_totp(
                stale,
                self.password,
            )

        persisted = self.store.load()

        self.assertTrue(
            persisted.totp_enabled
        )

        self.assertEqual(
            persisted.session_version,
            6,
        )

    def test_rejects_when_totp_is_not_enabled(self):
        password_only = self.admin.model_copy(
            update={
                "totp_enabled": False,
                "totp_secret_encrypted": None,
                "recovery_code_hashes": [],
                "totp_last_used_counter": None,
            }
        )

        self.store.save(
            password_only
        )

        with self.assertRaises(ValueError):
            self.service.disable_totp(
                password_only,
                self.password,
            )

        current = self.store.load()

        self.assertFalse(
            current.totp_enabled
        )

        self.assertEqual(
            current.session_version,
            5,
        )


if __name__ == "__main__":
    unittest.main()
