import tempfile
import threading
import unittest

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.models.admin import AdminAccount
from app.security.recovery_codes import (
    hash_recovery_code,
)
from app.services.admin_auth_service import (
    AdminAuthService,
)
from app.stores.admin_store import AdminStore


class AdminRecoveryCodeTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        self.addCleanup(
            self.temp_dir.cleanup
        )

        self.store_path = (
            Path(self.temp_dir.name)
            / "admin.json"
        )

        self.store = AdminStore(
            path=str(self.store_path)
        )

        self.service = AdminAuthService()
        self.service._store = self.store

        self.recovery_code = (
            "AAAA-BBBB-CCCC-DDDD-EEEE-FFFF"
        )

        self.other_recovery_code = (
            "2222-3333-4444-5555-6666-7777"
        )

        self.recovery_code_hash = (
            hash_recovery_code(
                self.recovery_code
            )
        )

        self.other_recovery_code_hash = (
            hash_recovery_code(
                self.other_recovery_code
            )
        )

        self.admin = AdminAccount(
            username="test-admin",
            password_hash="test-password-hash",
            created_at="2026-09-28T00:00:00+00:00",
            enabled=True,
            totp_enabled=True,
            totp_secret_encrypted=(
                "encrypted-test-secret"
            ),
            recovery_code_hashes=[
                self.recovery_code_hash,
                self.other_recovery_code_hash,
            ],
            totp_last_used_counter=100,
            session_version=5,
        )

        self.store.save(
            self.admin
        )

    def test_valid_recovery_code_creates_session_and_consumes_code(
        self,
    ):
        old_session = (
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

        session = self.service.create_session(
            self.admin,
            recovery_code=self.recovery_code,
        )

        current = self.store.load()

        self.assertEqual(
            current.session_version,
            6,
        )

        self.assertNotIn(
            self.recovery_code_hash,
            current.recovery_code_hashes,
        )

        self.assertIn(
            self.other_recovery_code_hash,
            current.recovery_code_hashes,
        )

        self.assertIsNotNone(
            self.service.verify_session(
                session
            )
        )

        self.assertIsNone(
            self.service.verify_session(
                old_session
            )
        )

    def test_recovery_code_cannot_be_reused(self):
        self.service.create_session(
            self.admin,
            recovery_code=self.recovery_code,
        )

        current = self.store.load()

        with self.assertRaises(ValueError):
            self.service.create_session(
                current,
                recovery_code=self.recovery_code,
            )

        after_reuse_attempt = (
            self.store.load()
        )

        self.assertEqual(
            after_reuse_attempt.session_version,
            current.session_version,
        )

        self.assertEqual(
            after_reuse_attempt.recovery_code_hashes,
            current.recovery_code_hashes,
        )

    def test_invalid_recovery_code_does_not_change_account(
        self,
    ):
        with self.assertRaises(ValueError):
            self.service.create_session(
                self.admin,
                recovery_code=(
                    "ZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZ-ZZZZ"
                ),
            )

        current = self.store.load()

        self.assertEqual(
            current.session_version,
            self.admin.session_version,
        )

        self.assertEqual(
            current.recovery_code_hashes,
            self.admin.recovery_code_hashes,
        )

    def test_recovery_code_is_rejected_without_totp(
        self,
    ):
        password_only_admin = (
            self.admin.model_copy(
                update={
                    "totp_enabled": False,
                    "totp_secret_encrypted": None,
                    "recovery_code_hashes": [],
                    "totp_last_used_counter": None,
                }
            )
        )

        self.store.save(
            password_only_admin
        )

        with self.assertRaises(ValueError):
            self.service.create_session(
                password_only_admin,
                recovery_code=self.recovery_code,
            )

    def test_totp_and_recovery_code_cannot_be_supplied_together(
        self,
    ):
        with self.assertRaises(ValueError):
            self.service.create_session(
                self.admin,
                totp_code="123456",
                recovery_code=self.recovery_code,
            )

        current = self.store.load()

        self.assertEqual(
            current.session_version,
            self.admin.session_version,
        )

        self.assertEqual(
            current.recovery_code_hashes,
            self.admin.recovery_code_hashes,
        )

    def test_concurrent_requests_cannot_reuse_recovery_code(
        self,
    ):
        service_a = AdminAuthService()
        service_a._store = AdminStore(
            path=str(self.store_path)
        )

        service_b = AdminAuthService()
        service_b._store = AdminStore(
            path=str(self.store_path)
        )

        barrier = threading.Barrier(2)

        def attempt(
            service: AdminAuthService,
        ) -> str | None:
            barrier.wait()

            try:
                return service.create_session(
                    self.admin,
                    recovery_code=self.recovery_code,
                )

            except ValueError:
                return None

        with ThreadPoolExecutor(
            max_workers=2
        ) as executor:
            futures = [
                executor.submit(
                    attempt,
                    service_a,
                ),
                executor.submit(
                    attempt,
                    service_b,
                ),
            ]

            sessions = [
                future.result()
                for future in futures
            ]

        successful_sessions = [
            session
            for session in sessions
            if session is not None
        ]

        self.assertEqual(
            len(successful_sessions),
            1,
        )

        current = self.store.load()

        self.assertEqual(
            current.session_version,
            6,
        )

        self.assertNotIn(
            self.recovery_code_hash,
            current.recovery_code_hashes,
        )

        self.assertIn(
            self.other_recovery_code_hash,
            current.recovery_code_hashes,
        )

        self.assertIsNotNone(
            self.service.verify_session(
                successful_sessions[0]
            )
        )


if __name__ == "__main__":
    unittest.main()
