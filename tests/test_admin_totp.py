import os
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

import pyotp

from cryptography.fernet import Fernet


TEST_TIMESTAMP = 1700000000


class AdminTotpTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_env = {
            "API_KEY": "test-api-key",
            "ADMIN_SESSION_SECRET":
                "test-session-secret-do-not-use",
            "SUPLA_CLIENT_ID": "test-client",
            "SUPLA_CLIENT_SECRET":
                "test-client-secret",
            "SUPLA_REDIRECT_URI":
                "http://localhost/test",
            "SUPLA_SCOPE": "test",
        }

        with patch.dict(os.environ, test_env):
            from app.config import settings
            from app.models.admin import AdminAccount
            from app.security.totp_crypto import (
                TotpSecretCipher,
            )
            from app.services.admin_auth_service import (
                AdminAuthService,
            )
            from app.stores.admin_store import AdminStore

        cls.settings = settings
        cls.AdminAccount = AdminAccount
        cls.TotpSecretCipher = TotpSecretCipher
        cls.AdminAuthService = AdminAuthService
        cls.AdminStore = AdminStore

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.addCleanup(
            self.temp_dir.cleanup
        )

        admin_path = (
            Path(self.temp_dir.name)
            / "admin.json"
        )

        self.store = self.AdminStore(
            path=str(admin_path)
        )

        self.service = self.AdminAuthService()

        # Never use the production administrator file.
        self.service._store = self.store

        self.key = Fernet.generate_key().decode(
            "ascii"
        )

        self.key_patch = patch.object(
            self.settings,
            "totp_encryption_key",
            self.key,
        )

        self.key_patch.start()
        self.addCleanup(self.key_patch.stop)

        self.secret = "JBSWY3DPEHPK3PXP"

        self.cipher = self.TotpSecretCipher(
            self.key
        )

        self.encrypted_secret = self.cipher.encrypt(
            self.secret
        )

        self.password = "test-password-123"

        self.admin = self.AdminAccount(
            username="test-admin",
            password_hash=(
                self.service._password_hash.hash(
                    self.password
                )
            ),
            created_at="2026-09-27T00:00:00+00:00",
            enabled=True,
            totp_enabled=True,
            totp_secret_encrypted=(
                self.encrypted_secret
            ),
        )

        self.store.save(self.admin)

        self.valid_code = pyotp.TOTP(
            self.secret
        ).at(TEST_TIMESTAMP)

        self.expected_counter = (
            TEST_TIMESTAMP // 30
        )

    def verify_at_test_time(
        self,
        admin,
        code,
    ):
        # Freeze TOTP verification time so the
        # tests do not depend on the real clock.

        with patch(
            "app.security.totp_service.time.time",
            return_value=TEST_TIMESTAMP,
        ):
            return self.service.verify_totp_code(
                admin,
                code,
            )

    def test_accepts_valid_totp_code(self):
        result = self.verify_at_test_time(
            self.admin,
            self.valid_code,
        )

        self.assertTrue(result)

        loaded = self.store.load()

        self.assertEqual(
            loaded.totp_last_used_counter,
            self.expected_counter,
        )

    def test_rejects_reused_totp_code(self):
        first = self.verify_at_test_time(
            self.admin,
            self.valid_code,
        )

        second = self.verify_at_test_time(
            self.admin,
            self.valid_code,
        )

        self.assertTrue(first)
        self.assertFalse(second)

    def test_rejects_invalid_totp_code(self):
        result = self.verify_at_test_time(
            self.admin,
            "invalid",
        )

        self.assertFalse(result)

        loaded = self.store.load()

        self.assertIsNone(
            loaded.totp_last_used_counter
        )

    def test_rejects_totp_when_disabled(self):
        disabled_admin = self.admin.model_copy(
            update={
                "totp_enabled": False,
            }
        )

        self.store.save(
            disabled_admin
        )

        result = self.verify_at_test_time(
            self.admin,
            self.valid_code,
        )

        self.assertFalse(result)

    def test_rejects_missing_encryption_key(self):
        with patch.object(
            self.settings,
            "totp_encryption_key",
            None,
        ):
            result = self.verify_at_test_time(
                self.admin,
                self.valid_code,
            )

        self.assertFalse(result)

    def test_rejects_wrong_encryption_key(self):
        wrong_key = Fernet.generate_key().decode(
            "ascii"
        )

        with patch.object(
            self.settings,
            "totp_encryption_key",
            wrong_key,
        ):
            result = self.verify_at_test_time(
                self.admin,
                self.valid_code,
            )

        self.assertFalse(result)

    def test_rejects_stale_password(self):
        updated_admin = self.admin.model_copy(
            update={
                "password_hash": (
                    self.service._password_hash.hash(
                        "different-test-password"
                    )
                ),
            }
        )

        self.store.save(
            updated_admin
        )

        result = self.verify_at_test_time(
            self.admin,
            self.valid_code,
        )

        self.assertFalse(result)

    def test_rejects_stale_totp_secret(self):
        updated_admin = self.admin.model_copy(
            update={
                "totp_secret_encrypted": (
                    self.cipher.encrypt(
                        pyotp.random_base32()
                    )
                ),
            }
        )

        self.store.save(
            updated_admin
        )

        result = self.verify_at_test_time(
            self.admin,
            self.valid_code,
        )

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
