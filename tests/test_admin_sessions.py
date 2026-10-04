
import tempfile
import time
import unittest

from pathlib import Path
from unittest.mock import patch

import pyotp

from cryptography.fernet import Fernet

from app.config import settings
from app.models.admin import AdminAccount
from app.security.totp_crypto import TotpSecretCipher
from app.services.admin_auth_service import AdminAuthService
from app.stores.admin_store import AdminStore


class AdminSessionTests(unittest.TestCase):

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
            created_at="2026-09-27T00:00:00+00:00",
        )

        self.store.save(self.admin)

        self.key = Fernet.generate_key().decode(
            "ascii"
        )

        self.key_patch = patch.object(
            settings,
            "totp_encryption_key",
            self.key,
        )

        self.key_patch.start()

        self.addCleanup(
            self.key_patch.stop
        )

        self.secret = "JBSWY3DPEHPK3PXP"

    def enable_totp(
        self,
        *,
        increment_version=True,
    ):
        admin = self.store.load()

        cipher = TotpSecretCipher(
            self.key
        )

        updated = admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted": (
                    cipher.encrypt(
                        self.secret
                    )
                ),
                "session_version": (
                    admin.session_version + 1
                    if increment_version
                    else admin.session_version
                ),
            }
        )

        self.store.save(
            updated
        )

        return updated

    def test_creates_versioned_session(self):
        session = self.service.create_session(
            self.admin
        )

        payload = self.service._serializer.loads(
            session
        )

        self.assertEqual(
            payload["session_version"],
            0,
        )

        self.assertFalse(
            payload["totp_verified"]
        )

        self.assertIsNotNone(
            self.service.verify_session(
                session
            )
        )

    def test_session_version_change_invalidates_session(self):
        session = self.service.create_session(
            self.admin
        )

        updated = self.admin.model_copy(
            update={
                "session_version": 1,
            }
        )

        self.store.save(
            updated
        )

        self.assertIsNone(
            self.service.verify_session(
                session
            )
        )

    def test_rejects_unversioned_session(self):
        unversioned_session = (
            self.service._serializer.dumps(
                {
                    "username": "test-admin",
                }
            )
        )

        self.assertIsNone(
            self.service.verify_session(
                unversioned_session
            )
        )

    def test_rejects_stale_admin_snapshot(self):
        updated = self.admin.model_copy(
            update={
                "session_version": 1,
            }
        )

        self.store.save(
            updated
        )

        with self.assertRaises(ValueError):
            self.service.create_session(
                self.admin
            )

    def test_old_session_rejected_after_enabling_totp(self):
        session = self.service.create_session(
            self.admin
        )

        # Even if someone forgets to increment
        # session_version, the old password-only
        # session must not bypass TOTP.

        self.enable_totp(
            increment_version=False
        )

        self.assertIsNone(
            self.service.verify_session(
                session
            )
        )

    def test_totp_cannot_be_skipped(self):
        secured_admin = self.enable_totp()

        with self.assertRaises(ValueError):
            self.service.create_session(
                secured_admin
            )

    def test_valid_totp_creates_authenticated_session(self):
        secured_admin = self.enable_totp()

        timestamp = int(
            time.time()
        )

        code = pyotp.TOTP(
            self.secret
        ).at(timestamp)

        session = self.service.create_session(
            secured_admin,
            totp_code=code,
        )

        payload = self.service._serializer.loads(
            session
        )

        self.assertTrue(
            payload["totp_verified"]
        )

        self.assertEqual(
            payload["session_version"],
            secured_admin.session_version,
        )

        self.assertIsNotNone(
            self.service.verify_session(
                session
            )
        )

    def test_reused_totp_cannot_create_second_session(self):
        secured_admin = self.enable_totp()

        code = pyotp.TOTP(
            self.secret
        ).now()

        self.service.create_session(
            secured_admin,
            totp_code=code,
        )

        with self.assertRaises(ValueError):
            self.service.create_session(
                secured_admin,
                totp_code=code,
            )

    def test_version_change_revokes_totp_session(self):
        secured_admin = self.enable_totp()

        code = pyotp.TOTP(
            self.secret
        ).now()

        session = self.service.create_session(
            secured_admin,
            totp_code=code,
        )

        updated = self.store.load().model_copy(
            update={
                "session_version": (
                    secured_admin.session_version + 1
                ),
            }
        )

        self.store.save(
            updated
        )

        self.assertIsNone(
            self.service.verify_session(
                session
            )
        )


if __name__ == "__main__":
    unittest.main()
