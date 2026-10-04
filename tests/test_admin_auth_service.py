import json
import os
import tempfile
import unittest

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from unittest.mock import patch


class AdminAuthServiceTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_env = {
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
            from app.models.admin import AdminAccount
            from app.services.admin_auth_service import (
                AdminAuthService,
            )
            from app.stores.admin_store import AdminStore

        cls.AdminAccount = AdminAccount
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

        # Isolate tests from production admin.json.
        self.service._store = self.store

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
        )

        self.store.save(self.admin)

    def test_accepts_valid_credentials(self):
        result = self.service.verify_credentials(
            "test-admin",
            self.password,
        )

        self.assertIsNotNone(result)

        self.assertEqual(
            result.username,
            "test-admin",
        )

    def test_rejects_invalid_credentials(self):
        self.assertIsNone(
            self.service.verify_credentials(
                "test-admin",
                "incorrect-password",
            )
        )

        self.assertIsNone(
            self.service.verify_credentials(
                "unknown-admin",
                self.password,
            )
        )

    def test_rejects_modified_session(self):
        session = self.service.create_session(
            self.admin
        )

        self.assertIsNotNone(
            self.service.verify_session(
                session
            )
        )

        self.assertIsNone(
            self.service.verify_session(
                session + ".invalid"
            )
        )

    def test_disabling_admin_invalidates_session(self):
        session = self.service.create_session(
            self.admin
        )

        disabled_admin = self.admin.model_copy(
            update={
                "enabled": False,
            }
        )

        self.store.save(
            disabled_admin
        )

        self.assertIsNone(
            self.service.verify_session(
                session
            )
        )

    def test_csrf_token_is_bound_to_session(self):
        session = self.service.create_session(
            self.admin
        )

        csrf_token = (
            self.service.create_csrf_token(
                session
            )
        )

        self.assertTrue(
            self.service.verify_csrf_token(
                session,
                csrf_token,
            )
        )

        self.assertFalse(
            self.service.verify_csrf_token(
                session,
                "invalid-csrf-token",
            )
        )

    def test_incomplete_admin_configuration_is_rejected(self):
        incomplete_admin = {
            "username": "test-admin",
            "password_hash": self.admin.password_hash,
            "created_at": "2026-09-27T00:00:00+00:00",
            "enabled": True,
        }

        with self.store.path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                incomplete_admin,
                file,
            )

        loaded = self.store.load()

        self.assertIsNone(
            loaded
        )

    def test_two_factor_metadata_persists(self):
        updated = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "test-encrypted-value",
                "recovery_code_hashes": [
                    "test-hash",
                ],
                "session_version": 1,
            }
        )

        self.store.save(
            updated
        )

        loaded = self.store.load()

        self.assertIsNotNone(loaded)

        self.assertTrue(
            loaded.totp_enabled
        )

        self.assertEqual(
            loaded.totp_secret_encrypted,
            "test-encrypted-value",
        )

        self.assertEqual(
            loaded.recovery_code_hashes,
            ["test-hash"],
        )

        self.assertEqual(
            loaded.session_version,
            1,
        )

    def test_totp_counter_is_consumed_only_once(self):
        admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
            }
        )

        self.store.save(
            admin
        )

        self.assertTrue(
            self.store.consume_totp_counter(
                "test-admin",
                "encrypted-test-secret",
                100,
            )
        )

        self.assertFalse(
            self.store.consume_totp_counter(
                "test-admin",
                "encrypted-test-secret",
                100,
            )
        )

        loaded = self.store.load()

        self.assertEqual(
            loaded.totp_last_used_counter,
            100,
        )

    def test_stale_save_cannot_rollback_totp_counter(self):
        admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
            }
        )

        self.store.save(
            admin
        )

        stale_admin = self.store.load()

        self.assertTrue(
            self.store.consume_totp_counter(
                "test-admin",
                "encrypted-test-secret",
                200,
            )
        )

        self.store.save(
            stale_admin
        )

        loaded = self.store.load()

        self.assertEqual(
            loaded.totp_last_used_counter,
            200,
        )

    def test_old_secret_cannot_consume_counter(self):
        admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "new-encrypted-secret",
            }
        )

        self.store.save(
            admin
        )

        self.assertFalse(
            self.store.consume_totp_counter(
                "test-admin",
                "old-encrypted-secret",
                100,
            )
        )

        self.assertTrue(
            self.store.consume_totp_counter(
                "test-admin",
                "new-encrypted-secret",
                100,
            )
        )

    def test_concurrent_requests_cannot_reuse_counter(self):
        admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
            }
        )

        self.store.save(
            admin
        )

        second_store = self.AdminStore(
            path=str(self.store.path)
        )

        barrier = Barrier(2)

        def consume(store):
            barrier.wait(
                timeout=5
            )

            return store.consume_totp_counter(
                "test-admin",
                "encrypted-test-secret",
                300,
            )

        with ThreadPoolExecutor(
            max_workers=2
        ) as executor:
            first = executor.submit(
                consume,
                self.store,
            )

            second = executor.submit(
                consume,
                second_store,
            )

            results = [
                first.result(),
                second.result(),
            ]

        self.assertEqual(
            results.count(True),
            1,
        )

        self.assertEqual(
            results.count(False),
            1,
        )

        loaded = self.store.load()

        self.assertEqual(
            loaded.totp_last_used_counter,
            300,
        )


if __name__ == "__main__":
    unittest.main()
