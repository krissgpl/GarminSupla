import io
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from app.models.admin import AdminAccount
from app.stores.admin_store import AdminStore
from scripts.reset_admin_2fa import (
    main,
    reset_admin_2fa,
)


class AdminTwoFactorResetScriptTests(
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
            password_hash="test-password-hash",
            created_at=(
                "2026-09-29T00:00:00+00:00"
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

    def test_reset_clears_two_factor_material(self):
        updated = reset_admin_2fa(
            self.store,
            self.admin,
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

        self.assertEqual(
            self.store.load(),
            updated,
        )

    def test_stale_snapshot_cannot_reset_two_factor(
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
            reset_admin_2fa(
                self.store,
                stale,
            )

        persisted = self.store.load()

        self.assertTrue(
            persisted.totp_enabled
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

        self.assertTrue(
            current.totp_enabled
        )

        self.assertEqual(
            current.session_version,
            5,
        )

    def test_main_resets_two_factor_after_confirmation(
        self,
    ):
        with (
            patch(
                "builtins.input",
                return_value="RESET",
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

        self.assertFalse(
            current.totp_enabled
        )

        self.assertEqual(
            current.session_version,
            6,
        )

        output = stdout.getvalue()

        self.assertIn(
            "Administrator 2FA reset successfully.",
            output,
        )

        self.assertNotIn(
            "encrypted-test-secret",
            output,
        )

        self.assertNotIn(
            "v1$recovery-one",
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

    def test_main_rejects_already_disabled_two_factor(
        self,
    ):
        disabled = self.admin.model_copy(
            update={
                "totp_enabled": False,
                "totp_secret_encrypted": None,
                "recovery_code_hashes": [],
                "totp_last_used_counter": None,
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

        self.assertFalse(
            current.totp_enabled
        )

        self.assertEqual(
            current.session_version,
            5,
        )


if __name__ == "__main__":
    unittest.main()
