import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient

from app.models.admin import AdminAccount
from app.routers.web import admin_auth
from app.security.admin_login_rate_limit import (
    AdminLoginRateLimiter,
)


class AdminLoginRateLimitIntegrationTests(
    unittest.TestCase
):
    def setUp(self):
        app = FastAPI()
        app.mount(
            "/static",
            StaticFiles(directory="static"),
            name="static",
        )
        app.include_router(admin_auth.router)

        self.client = TestClient(
            app,
            base_url="https://testserver",
        )

        self.admin = AdminAccount(
            username="test-admin",
            password_hash="test-hash",
            created_at="2026-09-28T00:00:00+00:00",
        )

        patches = (
            patch.object(
                admin_auth.setup_service,
                "load_settings",
                return_value=SimpleNamespace(
                    ui=SimpleNamespace(
                        language="en",
                        theme="light",
                    ),
                ),
            ),
            patch.object(
                admin_auth.settings,
                "admin_login_rate_limit_enabled",
                True,
            ),
            patch.object(
                admin_auth.settings,
                "admin_login_trusted_proxy_ips",
                "192.0.2.10",
            ),
            patch.object(
                admin_auth,
                "_admin_login_limiter",
                AdminLoginRateLimiter(
                    failure_limit=2,
                    window_seconds=60,
                    clock=lambda: 1000.0,
                ),
            ),
        )

        for item in patches:
            item.start()
            self.addCleanup(item.stop)

    def _invalid_password(self, headers=None):
        return self.client.post(
            "/login",
            data={
                "username": "test-admin",
                "password": "invalid-password",
            },
            headers=headers or {},
            follow_redirects=False,
        )

    def _totp(self):
        return self.client.post(
            "/login/totp",
            data={"code": "000000"},
            headers={
                "cookie": (
                    "garminsupla_totp_challenge="
                    "test-challenge"
                ),
            },
            follow_redirects=False,
        )

    def _recovery(self):
        return self.client.post(
            "/login/totp/recovery",
            data={"recovery_code": "invalid-code"},
            headers={
                "cookie": (
                    "garminsupla_totp_challenge="
                    "test-challenge"
                ),
            },
            follow_redirects=False,
        )

    def test_bad_password_triggers_429(self):
        with patch.object(
            admin_auth.admin_auth_service,
            "verify_credentials",
            return_value=None,
        ) as verify:
            first = self._invalid_password()
            second = self._invalid_password()

            blocked = self._invalid_password(
                headers={
                    "X-Real-IP": "198.51.100.123",
                },
            )

        self.assertEqual(first.status_code, 401)
        self.assertEqual(second.status_code, 401)
        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(
            blocked.headers.get("retry-after"),
            "60",
        )
        self.assertEqual(verify.call_count, 2)

    def test_password_and_totp_share_failure_budget(self):
        with (
            patch.object(
                admin_auth.admin_auth_service,
                "verify_credentials",
                return_value=None,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "verify_totp_challenge",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_session",
                side_effect=ValueError(
                    "Invalid additional factor."
                ),
            ) as create_session,
        ):
            password = self._invalid_password()
            totp = self._totp()
            recovery = self._recovery()

        self.assertEqual(password.status_code, 401)
        self.assertEqual(totp.status_code, 401)
        self.assertEqual(recovery.status_code, 429)
        self.assertEqual(
            create_session.call_count,
            1,
        )

    def test_recovery_failures_trigger_429(self):
        with (
            patch.object(
                admin_auth.admin_auth_service,
                "verify_totp_challenge",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_session",
                side_effect=ValueError(
                    "Invalid recovery code."
                ),
            ) as create_session,
        ):
            first = self._recovery()
            second = self._recovery()
            blocked = self._recovery()

        self.assertEqual(first.status_code, 401)
        self.assertEqual(second.status_code, 401)
        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(
            create_session.call_count,
            2,
        )

    def test_disabled_flag_preserves_login_behavior(self):
        with (
            patch.object(
                admin_auth.settings,
                "admin_login_rate_limit_enabled",
                False,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "verify_credentials",
                return_value=None,
            ) as verify,
        ):
            statuses = [
                self._invalid_password().status_code
                for _ in range(4)
            ]

        self.assertEqual(statuses, [401] * 4)
        self.assertEqual(verify.call_count, 4)


if __name__ == "__main__":
    unittest.main()
