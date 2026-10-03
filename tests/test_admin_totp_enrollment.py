import tempfile
import unittest

from pathlib import Path
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

import pyotp

from cryptography.fernet import Fernet

from app.config import settings
from app.models.admin import AdminAccount
from app.security.recovery_codes import (
    RECOVERY_CODE_COUNT,
    hash_recovery_code,
)
from app.security.totp_crypto import TotpSecretCipher
from app.services.admin_auth_service import (
    AdminAuthService,
)
from app.stores.admin_store import AdminStore


class AdminTotpEnrollmentTests(unittest.TestCase):

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
        )

        self.store.save(
            self.admin
        )

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

    def create_enrollment(
        self,
    ) -> tuple[str, str, str, str]:
        token, provisioning_uri = (
            self.service.create_totp_enrollment(
                self.admin,
                self.password,
            )
        )

        parsed = urlparse(
            provisioning_uri
        )

        query = parse_qs(
            parsed.query
        )

        secret = query["secret"][0]

        code = pyotp.TOTP(
            secret
        ).now()

        return (
            token,
            provisioning_uri,
            secret,
            code,
        )

    def test_creates_totp_enrollment(self):
        token, provisioning_uri = (
            self.service.create_totp_enrollment(
                self.admin,
                self.password,
            )
        )

        self.assertTrue(
            token
        )

        parsed = urlparse(
            provisioning_uri
        )

        self.assertEqual(
            parsed.scheme,
            "otpauth",
        )

        self.assertEqual(
            parsed.netloc,
            "totp",
        )

        query = parse_qs(
            parsed.query
        )

        self.assertEqual(
            query["issuer"],
            ["GarminSupla"],
        )

        self.assertIn(
            "secret",
            query,
        )

    def test_pending_secret_is_not_persisted(self):
        self.service.create_totp_enrollment(
            self.admin,
            self.password,
        )

        current = self.store.load()

        self.assertFalse(
            current.totp_enabled
        )

        self.assertIsNone(
            current.totp_secret_encrypted
        )

        self.assertIsNone(
            current.totp_last_used_counter
        )

        self.assertEqual(
            current.session_version,
            0,
        )

        self.assertEqual(
            current.recovery_code_hashes,
            [],
        )


    def test_enrollment_token_contains_encrypted_secret(self):
        token, provisioning_uri = (
            self.service.create_totp_enrollment(
                self.admin,
                self.password,
            )
        )

        payload = (
            self.service
            ._totp_enrollment_serializer
            .loads(token)
        )

        encrypted_secret = payload.get(
            "encrypted_secret"
        )

        self.assertIsInstance(
            encrypted_secret,
            str,
        )

        cipher = TotpSecretCipher(
            self.key
        )

        secret = cipher.decrypt(
            encrypted_secret
        )

        parsed = urlparse(
            provisioning_uri
        )

        query = parse_qs(
            parsed.query
        )

        self.assertEqual(
            query["secret"],
            [secret],
        )

        self.assertNotIn(
            secret,
            token,
        )

    def test_rejects_wrong_password(self):
        with self.assertRaises(ValueError):
            self.service.create_totp_enrollment(
                self.admin,
                "wrong-password",
            )

    def test_rejects_when_totp_already_enabled(self):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "already-configured",
                "session_version": 1,
            }
        )

        self.store.save(
            secured_admin
        )

        with self.assertRaises(ValueError):
            self.service.create_totp_enrollment(
                secured_admin,
                self.password,
            )

    def test_rejects_missing_encryption_key(self):
        with patch.object(
            settings,
            "totp_encryption_key",
            None,
        ):
            with self.assertRaises(ValueError):
                self.service.create_totp_enrollment(
                    self.admin,
                    self.password,
                )

    def test_rejects_stale_admin_snapshot(self):
        stale_admin = self.store.load()

        updated = stale_admin.model_copy(
            update={
                "session_version": 1,
            }
        )

        self.store.save(
            updated
        )

        with self.assertRaises(ValueError):
            self.service.create_totp_enrollment(
                stale_admin,
                self.password,
            )

    def test_confirms_totp_enrollment(self):
        token, _, secret, code = (
            self.create_enrollment()
        )

        (
            confirmed,
            recovery_codes,
        ) = self.service.confirm_totp_enrollment(
            token,
            code,
        )

        self.assertTrue(
            confirmed.totp_enabled
        )

        self.assertIsNotNone(
            confirmed.totp_secret_encrypted
        )

        self.assertIsNotNone(
            confirmed.totp_last_used_counter
        )

        self.assertEqual(
            confirmed.session_version,
            1,
        )

        cipher = TotpSecretCipher(
            self.key
        )

        stored_secret = cipher.decrypt(
            confirmed.totp_secret_encrypted
        )

        self.assertEqual(
            stored_secret,
            secret,
        )

        self.assertEqual(
            len(recovery_codes),
            RECOVERY_CODE_COUNT,
        )

        self.assertEqual(
            len(confirmed.recovery_code_hashes),
            RECOVERY_CODE_COUNT,
        )

    def test_confirmation_persists_first_used_counter(self):
        token, _, _, code = (
            self.create_enrollment()
        )

        (
            confirmed,
            _,
        ) = self.service.confirm_totp_enrollment(
            token,
            code,
        )

        self.assertFalse(
            self.service.verify_totp_code(
                confirmed,
                code,
            )
        )

    def test_confirmation_invalidates_existing_session(self):
        session = self.service.create_session(
            self.admin
        )

        token, _, _, code = (
            self.create_enrollment()
        )

        self.assertIsNotNone(
            self.service.verify_session(
                session
            )
        )

        self.service.confirm_totp_enrollment(
            token,
            code,
        )

        self.assertIsNone(
            self.service.verify_session(
                session
            )
        )

    def test_rejects_invalid_confirmation_code(self):
        token, _, _, _ = (
            self.create_enrollment()
        )

        with self.assertRaises(ValueError):
            self.service.confirm_totp_enrollment(
                token,
                "invalid",
            )

        current = self.store.load()

        self.assertFalse(
            current.totp_enabled
        )

        self.assertIsNone(
            current.totp_secret_encrypted
        )

    def test_rejects_modified_enrollment_token(self):
        token, _, _, code = (
            self.create_enrollment()
        )

        with self.assertRaises(ValueError):
            self.service.confirm_totp_enrollment(
                token + ".invalid",
                code,
            )

        self.assertFalse(
            self.store.load().totp_enabled
        )

    def test_rejects_reused_enrollment_token(self):
        token, _, _, code = (
            self.create_enrollment()
        )

        self.service.confirm_totp_enrollment(
            token,
            code,
        )

        with self.assertRaises(ValueError):
            self.service.confirm_totp_enrollment(
                token,
                code,
            )

    def test_rejects_stale_enrollment_token(self):
        token, _, _, code = (
            self.create_enrollment()
        )

        current = self.store.load()

        updated = current.model_copy(
            update={
                "session_version":
                    current.session_version + 1,
            }
        )

        self.store.save(
            updated
        )

        with self.assertRaises(ValueError):
            self.service.confirm_totp_enrollment(
                token,
                code,
            )

        self.assertFalse(
            self.store.load().totp_enabled
        )

    def test_confirmation_generates_recovery_codes(self):
        token, _, _, code = (
            self.create_enrollment()
        )

        (
            confirmed,
            recovery_codes,
        ) = self.service.confirm_totp_enrollment(
            token,
            code,
        )

        self.assertEqual(
            len(recovery_codes),
            RECOVERY_CODE_COUNT,
        )

        self.assertEqual(
            len(set(recovery_codes)),
            RECOVERY_CODE_COUNT,
        )

        self.assertEqual(
            len(confirmed.recovery_code_hashes),
            RECOVERY_CODE_COUNT,
        )

        for recovery_code in recovery_codes:
            groups = recovery_code.split("-")

            self.assertEqual(
                len(groups),
                6,
            )

            self.assertTrue(
                all(
                    len(group) == 4
                    for group in groups
                )
            )

            self.assertIn(
                hash_recovery_code(
                    recovery_code
                ),
                confirmed.recovery_code_hashes,
            )

    def test_recovery_codes_are_not_persisted_in_plaintext(self):
        token, _, _, code = (
            self.create_enrollment()
        )

        (
            confirmed,
            recovery_codes,
        ) = self.service.confirm_totp_enrollment(
            token,
            code,
        )

        persisted = self.store.path.read_text(
            encoding="utf-8"
        )

        for recovery_code in recovery_codes:
            self.assertNotIn(
                recovery_code,
                persisted,
            )

            self.assertNotIn(
                recovery_code.replace(
                    "-",
                    "",
                ),
                persisted,
            )

        for recovery_hash in (
            confirmed.recovery_code_hashes
        ):
            self.assertIn(
                recovery_hash,
                persisted,
            )


if __name__ == "__main__":
    unittest.main()
