import io
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from pwdlib import PasswordHash

from app.models.admin import AdminAccount
from app.stores.admin_store import AdminStore
from scripts.reset_admin_password import (
    main,
    reset_admin_password,
)


class AdminPasswordResetScriptTests(
    unittest.TestCase
):

    def setUp(self):
        self.temp_dir = (
            tempfile.TemporaryDirectory()
        )

        self.addCleanup(
            self.temp_dir.cleanup
        )

        self.store = AdminStore(
            path=str(
                Path(self.temp_dir.name)
                / "admin.json"
            )
        )

        self.admin = AdminAccount(
            username="test-admin",
            password_hash="original-password-hash",
            created_at=(
                "2026-10-03T00:00:00+00:00"
            ),
            enabled=True,
            totp_enabled=True,
            totp_secret_encrypted=(
                "encrypted-test-secret"
            ),
            recovery_code_hashes=[
                "v1$recovery-one",
                "v1$recovery-two",
            ],
            totp_last_used_counter=123456,
            session_version=5,
        )

        self.store.save(
            self.admin
        )

    def test_reset_changes_password_and_preserves_two_factor(
        self,
    ):
        updated = reset_admin_password(
            self.store,
            self.admin,
            "new-password-hash",
        )

        self.assertEqual(
            updated.password_hash,
            "new-password-hash",
        )

        self.assertEqual(
            updated.session_version,
            6,
        )

        self.assertTrue(
            updated.totp_enabled
        )

        self.assertEqual(
            updated.totp_secret_encrypted,
            "encrypted-test-secret",
        )

        self.assertEqual(
            updated.recovery_code_hashes,
            [
                "v1$recovery-one",
                "v1$recovery-two",
            ],
        )

        self.assertEqual(
            updated.totp_last_used_counter,
            123456,
        )

        self.assertEqual(
            self.store.load(),
            updated,
        )

    def test_stale_snapshot_cannot_reset_password(
        self,
    ):
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
            reset_admin_password(
                self.store,
                stale,
                "new-password-hash",
            )

        persisted = self.store.load()

        self.assertEqual(
            persisted.password_hash,
            "original-password-hash",
        )

        self.assertEqual(
            persisted.session_version,
            6,
        )

    def test_main_requires_exact_confirmation(self):
        with (
            patch(
                "builtins.input",
                return_value="reset",
            ),
            patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ),
        ):
            with self.assertRaises(
                SystemExit
            ) as context:
                main(
                    self.store
                )

        self.assertEqual(
            context.exception.code,
            1,
        )

        current = self.store.load()

        self.assertEqual(
            current.password_hash,
            "original-password-hash",
        )

        self.assertEqual(
            current.session_version,
            5,
        )

    def test_main_rejects_password_mismatch(self):
        with (
            patch(
                "builtins.input",
                return_value="RESET",
            ),
            patch(
                "scripts.reset_admin_password.getpass",
                side_effect=[
                    "new-password-123",
                    "different-password-123",
                ],
            ),
            patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ),
        ):
            with self.assertRaises(
                SystemExit
            ) as context:
                main(
                    self.store
                )

        self.assertEqual(
            context.exception.code,
            1,
        )

        current = self.store.load()

        self.assertEqual(
            current.password_hash,
            "original-password-hash",
        )

        self.assertEqual(
            current.session_version,
            5,
        )

    def test_main_rejects_short_password(self):
        with (
            patch(
                "builtins.input",
                return_value="RESET",
            ),
            patch(
                "scripts.reset_admin_password.getpass",
                side_effect=[
                    "short",
                    "short",
                ],
            ),
            patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ),
        ):
            with self.assertRaises(
                SystemExit
            ) as context:
                main(
                    self.store
                )

        self.assertEqual(
            context.exception.code,
            1,
        )

        current = self.store.load()

        self.assertEqual(
            current.password_hash,
            "original-password-hash",
        )

        self.assertEqual(
            current.session_version,
            5,
        )

    def test_main_resets_password_after_confirmation(
        self,
    ):
        with (
            patch(
                "builtins.input",
                return_value="RESET",
            ),
            patch(
                "scripts.reset_admin_password.getpass",
                side_effect=[
                    "new-admin-password-123",
                    "new-admin-password-123",
                ],
            ),
            patch(
                "sys.stdout",
                new_callable=io.StringIO,
            ) as stdout,
        ):
            main(
                self.store
            )

        current = self.store.load()

        self.assertEqual(
            current.session_version,
            6,
        )

        password_hash = PasswordHash.recommended()

        self.assertTrue(
            password_hash.verify(
                "new-admin-password-123",
                current.password_hash,
            )
        )

        self.assertTrue(
            current.totp_enabled
        )

        self.assertEqual(
            current.totp_secret_encrypted,
            "encrypted-test-secret",
        )

        output = stdout.getvalue()

        self.assertIn(
            "Administrator password reset successfully.",
            output,
        )

        self.assertNotIn(
            "new-admin-password-123",
            output,
        )

        self.assertNotIn(
            current.password_hash,
            output,
        )

    def test_main_rejects_missing_admin(self):
        empty_store = AdminStore(
            path=str(
                Path(self.temp_dir.name)
                / "missing-admin.json"
            )
        )

        with patch(
            "sys.stdout",
            new_callable=io.StringIO,
        ):
            with self.assertRaises(
                SystemExit
            ) as context:
                main(
                    empty_store
                )

        self.assertEqual(
            context.exception.code,
            1,
        )

    def test_main_rejects_disabled_admin(self):
        disabled = self.admin.model_copy(
            update={
                "enabled": False,
            }
        )

        self.store.save(
            disabled
        )

        with patch(
            "sys.stdout",
            new_callable=io.StringIO,
        ):
            with self.assertRaises(
                SystemExit
            ) as context:
                main(
                    self.store
                )

        self.assertEqual(
            context.exception.code,
            1,
        )

        current = self.store.load()

        self.assertEqual(
            current.password_hash,
            "original-password-hash",
        )

        self.assertEqual(
            current.session_version,
            5,
        )


if __name__ == "__main__":
    unittest.main()
