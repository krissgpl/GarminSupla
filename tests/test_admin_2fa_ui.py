import unittest

from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient

from app.models.admin import AdminAccount
from app.routers.web import admin_auth


class AdminTwoFactorUiTests(unittest.TestCase):

    def setUp(self):
        app = FastAPI()

        app.mount(
            "/static",
            StaticFiles(
                directory="static"
            ),
            name="static",
        )

        app.include_router(
            admin_auth.router
        )

        self.client = TestClient(
            app,
            base_url="https://testserver",
        )

        self.admin = AdminAccount(
            username="test-admin",
            password_hash="test-hash",
            created_at="2026-09-28T00:00:00+00:00",
            enabled=True,
        )

        self.settings_patch = patch.object(
            admin_auth.setup_service,
            "load_settings",
            return_value=SimpleNamespace(
                ui=SimpleNamespace(
                    language="en",
                    theme="light",
                )
            ),
        )

        self.settings_patch.start()

        self.addCleanup(
            self.settings_patch.stop
        )

    def test_displays_password_confirmation_form(self):
        with patch.object(
            admin_auth,
            "require_admin_web",
            return_value=self.admin,
        ):
            response = self.client.get(
                "/security/2fa",
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            'action="/security/2fa/verify-password"',
            response.text,
        )

        self.assertIn(
            'name="password"',
            response.text,
        )

    def test_rejects_wrong_password(self):
        with (
            patch.object(
                admin_auth,
                "require_admin_web",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth,
                "verify_admin_csrf",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "verify_credentials",
                return_value=None,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_totp_enrollment",
            ) as create_enrollment,
        ):
            response = self.client.post(
                "/security/2fa/verify-password",
                data={
                    "password": "wrong-password",
                    "csrf_token": "test-csrf",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertIn(
            "Invalid password.",
            response.text,
        )

        create_enrollment.assert_not_called()

    def test_correct_password_starts_enrollment(self):
        provisioning_uri = (
            "otpauth://totp/"
            "GarminSupla%3Atest-admin"
            "?secret=TESTSECRET"
            "&issuer=GarminSupla"
        )

        with (
            patch.object(
                admin_auth,
                "require_admin_web",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth,
                "verify_admin_csrf",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "verify_credentials",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_totp_enrollment",
                return_value=(
                    "enrollment-token",
                    provisioning_uri,
                ),
            ) as create_enrollment,
        ):
            response = self.client.post(
                "/security/2fa/verify-password",
                data={
                    "password": "correct-password",
                    "csrf_token": "test-csrf",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        create_enrollment.assert_called_once_with(
            self.admin,
            "correct-password",
        )

        self.assertIn(
            "Authenticator application setup",
            response.text,
        )

        self.assertIn(
            "otpauth://totp/",
            response.text,
        )

        self.assertEqual(
            response.cookies.get(
                admin_auth.TOTP_ENROLLMENT_COOKIE
            ),
            "enrollment-token",
        )

        self.assertEqual(
            response.headers.get(
                "cache-control"
            ),
            "no-store, max-age=0",
        )

    def test_enrollment_token_is_not_rendered(self):
        provisioning_uri = (
            "otpauth://totp/"
            "GarminSupla%3Atest-admin"
            "?secret=TESTSECRET"
            "&issuer=GarminSupla"
        )

        with (
            patch.object(
                admin_auth,
                "require_admin_web",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth,
                "verify_admin_csrf",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "verify_credentials",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_totp_enrollment",
                return_value=(
                    "very-secret-enrollment-token",
                    provisioning_uri,
                ),
            ),
        ):
            response = self.client.post(
                "/security/2fa/verify-password",
                data={
                    "password": "correct-password",
                    "csrf_token": "test-csrf",
                },
            )

        self.assertNotIn(
            "very-secret-enrollment-token",
            response.text,
        )

        set_cookie = response.headers.get(
            "set-cookie",
            ""
        )

        self.assertIn(
            "HttpOnly",
            set_cookie,
        )

        self.assertIn(
            "Secure",
            set_cookie,
        )

    def test_enrollment_failure_returns_error(self):
        with (
            patch.object(
                admin_auth,
                "require_admin_web",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth,
                "verify_admin_csrf",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "verify_credentials",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_totp_enrollment",
                side_effect=ValueError(
                    "Enrollment unavailable."
                ),
            ),
        ):
            response = self.client.post(
                "/security/2fa/verify-password",
                data={
                    "password": "correct-password",
                    "csrf_token": "test-csrf",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            409,
        )

        self.assertIn(
            "Unable to start 2FA setup.",
            response.text,
        )

    def test_enabled_two_factor_shows_enabled_state(self):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
            }
        )

        with patch.object(
            admin_auth,
            "require_admin_web",
            return_value=secured_admin,
        ):
            response = self.client.get(
                "/security/2fa",
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "2FA is enabled",
            response.text,
        )

        self.assertIn(
            'action="/security/2fa/disable"',
            response.text,
        )

        self.assertIn(
            'name="password"',
            response.text,
        )


    def test_enrollment_renders_local_svg_qr_code(self):
        provisioning_uri = (
            "otpauth://totp/"
            "GarminSupla%3Atest-admin"
            "?secret=TESTSECRET"
            "&issuer=GarminSupla"
        )

        with (
            patch.object(
                admin_auth,
                "require_admin_web",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth,
                "verify_admin_csrf",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "verify_credentials",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_totp_enrollment",
                return_value=(
                    "enrollment-token",
                    provisioning_uri,
                ),
            ),
        ):
            response = self.client.post(
                "/security/2fa/verify-password",
                data={
                    "password": "correct-password",
                    "csrf_token": "test-csrf",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            'id="totp-qr-code"',
            response.text,
        )

        self.assertIn(
            'src="data:image/svg+xml',
            response.text,
        )

        self.assertIn(
            "otpauth://totp/",
            response.text,
        )


    def test_qr_generator_returns_svg_data_uri(self):
        provisioning_uri = (
            "otpauth://totp/"
            "GarminSupla%3Atest-admin"
            "?secret=TESTSECRET"
            "&issuer=GarminSupla"
        )

        qr_data_uri = (
            admin_auth._create_totp_qr_data_uri(
                provisioning_uri
            )
        )

        self.assertTrue(
            qr_data_uri.startswith(
                "data:image/svg+xml"
            )
        )


    def test_enrollment_displays_totp_confirmation_form(self):
        provisioning_uri = (
            "otpauth://totp/"
            "GarminSupla%3Atest-admin"
            "?secret=TESTSECRET"
            "&issuer=GarminSupla"
        )

        with (
            patch.object(
                admin_auth,
                "require_admin_web",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth,
                "verify_admin_csrf",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "verify_credentials",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_totp_enrollment",
                return_value=(
                    "enrollment-token",
                    provisioning_uri,
                ),
            ),
        ):
            response = self.client.post(
                "/security/2fa/verify-password",
                data={
                    "password": "correct-password",
                    "csrf_token": "test-csrf",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            'action="/security/2fa/confirm"',
            response.text,
        )

        self.assertIn(
            'name="code"',
            response.text,
        )

        self.assertIn(
            'autocomplete="one-time-code"',
            response.text,
        )

    def test_valid_confirmation_displays_recovery_codes(self):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
                "session_version": 1,
            }
        )

        recovery_codes = [
            "AAAA-BBBB-CCCC-DDDD-EEEE-FFFF",
            "GGGG-HHHH-JJJJ-KKKK-LLLL-MMMM",
        ]

        self.client.cookies.set(
            admin_auth.TOTP_ENROLLMENT_COOKIE,
            "enrollment-token",
            domain="testserver.local",
            path="/security/2fa",
        )

        self.client.cookies.set(
            admin_auth.SESSION_COOKIE,
            "session-token",
            domain="testserver.local",
            path="/",
        )

        self.client.cookies.set(
            admin_auth.CSRF_COOKIE,
            "csrf-token",
            domain="testserver.local",
            path="/",
        )

        with (
            patch.object(
                admin_auth,
                "require_admin_web",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth,
                "verify_admin_csrf",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "confirm_totp_enrollment",
                return_value=(
                    secured_admin,
                    recovery_codes,
                ),
            ) as confirm_enrollment,
        ):
            response = self.client.post(
                "/security/2fa/confirm",
                data={
                    "code": "123456",
                    "csrf_token": "csrf-token",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        confirm_enrollment.assert_called_once_with(
            "enrollment-token",
            "123456",
        )

        self.assertIn(
            "Save your recovery codes",
            response.text,
        )

        for recovery_code in recovery_codes:
            self.assertIn(
                recovery_code,
                response.text,
            )

        self.assertIn(
            'id="copy-recovery-codes"',
            response.text,
        )

        self.assertIn(
            "Copy all codes",
            response.text,
        )

        self.assertIn(
            "recovery-code",
            response.text,
        )

        self.assertEqual(
            response.headers.get(
                "cache-control"
            ),
            "no-store, max-age=0",
        )

        self.assertIsNone(
            self.client.cookies.get(
                admin_auth.SESSION_COOKIE
            )
        )

        self.assertIsNone(
            self.client.cookies.get(
                admin_auth.CSRF_COOKIE
            )
        )

        self.assertIsNone(
            self.client.cookies.get(
                admin_auth.TOTP_ENROLLMENT_COOKIE
            )
        )

    def test_invalid_confirmation_code_allows_retry(self):
        self.client.cookies.set(
            admin_auth.TOTP_ENROLLMENT_COOKIE,
            "enrollment-token",
            domain="testserver.local",
            path="/security/2fa",
        )

        with (
            patch.object(
                admin_auth,
                "require_admin_web",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth,
                "verify_admin_csrf",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "confirm_totp_enrollment",
                side_effect=ValueError(
                    "Invalid TOTP enrollment code."
                ),
            ),
        ):
            response = self.client.post(
                "/security/2fa/confirm",
                data={
                    "code": "000000",
                    "csrf_token": "test-csrf",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertIn(
            "Invalid or expired authentication code.",
            response.text,
        )

        self.assertIn(
            'action="/security/2fa/confirm"',
            response.text,
        )

        self.assertEqual(
            self.client.cookies.get(
                admin_auth.TOTP_ENROLLMENT_COOKIE
            ),
            "enrollment-token",
        )

        self.assertEqual(
            response.headers.get(
                "cache-control"
            ),
            "no-store, max-age=0",
        )

    def test_confirmation_requires_enrollment_cookie(self):
        with (
            patch.object(
                admin_auth,
                "require_admin_web",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth,
                "verify_admin_csrf",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "confirm_totp_enrollment",
            ) as confirm_enrollment,
        ):
            response = self.client.post(
                "/security/2fa/confirm",
                data={
                    "code": "123456",
                    "csrf_token": "test-csrf",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            303,
        )

        self.assertEqual(
            response.headers.get("location"),
            "/security/2fa",
        )

        confirm_enrollment.assert_not_called()

    def test_disable_two_factor_requires_password(self):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
                "session_version": 1,
            }
        )

        with patch.object(
            admin_auth,
            "require_admin_web",
            return_value=secured_admin,
        ):
            response = self.client.get(
                "/security/2fa",
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            'action="/security/2fa/disable"',
            response.text,
        )

        self.assertIn(
            'autocomplete="current-password"',
            response.text,
        )

    def test_valid_password_disables_two_factor_and_clears_session(
        self,
    ):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
                "session_version": 1,
            }
        )

        disabled_admin = secured_admin.model_copy(
            update={
                "totp_enabled": False,
                "totp_secret_encrypted": None,
                "recovery_code_hashes": [],
                "totp_last_used_counter": None,
                "session_version": 2,
            }
        )

        self.client.cookies.set(
            admin_auth.SESSION_COOKIE,
            "session-token",
            domain="testserver.local",
            path="/",
        )

        self.client.cookies.set(
            admin_auth.CSRF_COOKIE,
            "csrf-token",
            domain="testserver.local",
            path="/",
        )

        with (
            patch.object(
                admin_auth,
                "require_admin_web",
                return_value=secured_admin,
            ),
            patch.object(
                admin_auth,
                "verify_admin_csrf",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "disable_totp",
                return_value=disabled_admin,
            ) as disable_totp,
        ):
            response = self.client.post(
                "/security/2fa/disable",
                data={
                    "password": "correct-password",
                    "csrf_token": "csrf-token",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        disable_totp.assert_called_once_with(
            secured_admin,
            "correct-password",
        )

        self.assertIn(
            "2FA has been disabled",
            response.text,
        )

        self.assertIn(
            'href="/login"',
            response.text,
        )

        self.assertEqual(
            response.headers.get(
                "cache-control"
            ),
            "no-store, max-age=0",
        )

        self.assertIsNone(
            self.client.cookies.get(
                admin_auth.SESSION_COOKIE
            )
        )

        self.assertIsNone(
            self.client.cookies.get(
                admin_auth.CSRF_COOKIE
            )
        )

    def test_wrong_password_does_not_disable_two_factor(
        self,
    ):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
                "session_version": 1,
            }
        )

        self.client.cookies.set(
            admin_auth.SESSION_COOKIE,
            "session-token",
            domain="testserver.local",
            path="/",
        )

        with (
            patch.object(
                admin_auth,
                "require_admin_web",
                return_value=secured_admin,
            ),
            patch.object(
                admin_auth,
                "verify_admin_csrf",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "disable_totp",
                side_effect=ValueError(
                    "Password confirmation failed."
                ),
            ),
        ):
            response = self.client.post(
                "/security/2fa/disable",
                data={
                    "password": "wrong-password",
                    "csrf_token": "test-csrf",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertIn(
            "Unable to disable 2FA.",
            response.text,
        )

        self.assertIn(
            "2FA is enabled",
            response.text,
        )

        self.assertEqual(
            self.client.cookies.get(
                admin_auth.SESSION_COOKIE
            ),
            "session-token",
        )


if __name__ == "__main__":
    unittest.main()
