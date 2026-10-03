import unittest

from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient

from app.models.admin import AdminAccount
from app.routers.web import admin_auth


class AdminLoginFlowTests(unittest.TestCase):

    def setUp(self):
        app = FastAPI()

        app.mount(
            "/static",
            StaticFiles(directory="static"),
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
            password_hash="test-password-hash",
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

    def test_login_page_shows_first_install_instructions(
        self,
    ):
        with patch.object(
            admin_auth.admin_auth_service,
            "administrator_exists",
            return_value=False,
        ):
            response = self.client.get(
                "/login",
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            "Administrator account has not been created yet",
            response.text,
        )

        self.assertIn(
            (
                "docker compose exec garminsupla-api "
                "python -m scripts.create_admin"
            ),
            response.text,
        )

        self.assertNotIn(
            'action="/login"',
            response.text,
        )

    def test_login_page_displays_form_when_admin_exists(
        self,
    ):
        with patch.object(
            admin_auth.admin_auth_service,
            "administrator_exists",
            return_value=True,
        ):
            response = self.client.get(
                "/login",
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            'action="/login"',
            response.text,
        )

        self.assertIn(
            'name="username"',
            response.text,
        )

        self.assertIn(
            'name="password"',
            response.text,
        )

    def test_login_page_uses_saved_dark_theme(self):
        with patch.object(
            admin_auth.setup_service,
            "load_settings",
            return_value=SimpleNamespace(
                ui=SimpleNamespace(
                    language="en",
                    theme="dark",
                )
            ),
        ):
            response = self.client.get(
                "/login",
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            'data-ui-theme="dark"',
            response.text,
        )

        self.assertIn(
            'data-bs-theme="dark"',
            response.text,
        )

    def test_password_only_login_creates_session(self):
        with (
            patch.object(
                admin_auth.admin_auth_service,
                "verify_credentials",
                return_value=self.admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_session",
                return_value="session-token",
            ) as create_session,
            patch.object(
                admin_auth.admin_auth_service,
                "create_csrf_token",
                return_value="csrf-token",
            ),
        ):
            response = self.client.post(
                "/login",
                data={
                    "username": "test-admin",
                    "password": "test-password",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            303,
        )

        self.assertEqual(
            response.headers["location"],
            "/dashboard",
        )

        create_session.assert_called_once_with(
            self.admin
        )

        self.assertEqual(
            response.cookies.get(
                admin_auth.SESSION_COOKIE
            ),
            "session-token",
        )

    def test_totp_account_redirects_to_second_factor(self):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
            }
        )

        with (
            patch.object(
                admin_auth.admin_auth_service,
                "verify_credentials",
                return_value=secured_admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_totp_challenge",
                return_value="challenge-token",
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_session",
            ) as create_session,
        ):
            response = self.client.post(
                "/login",
                data={
                    "username": "test-admin",
                    "password": "test-password",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            303,
        )

        self.assertEqual(
            response.headers["location"],
            "/login/totp",
        )

        self.assertEqual(
            response.cookies.get(
                admin_auth.TOTP_CHALLENGE_COOKIE
            ),
            "challenge-token",
        )

        create_session.assert_not_called()

    def test_totp_page_requires_valid_challenge(self):
        response = self.client.get(
            "/login/totp",
            follow_redirects=False,
        )

        self.assertEqual(
            response.status_code,
            303,
        )

        self.assertEqual(
            response.headers["location"],
            "/login",
        )

    def test_totp_page_is_displayed_for_valid_challenge(self):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
            }
        )

        self.client.cookies.set(
            admin_auth.TOTP_CHALLENGE_COOKIE,
            "challenge-token",
            domain="testserver.local",
            path="/login/totp",
        )

        with patch.object(
            admin_auth.admin_auth_service,
            "verify_totp_challenge",
            return_value=secured_admin,
        ):
            response = self.client.get(
                "/login/totp",
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            'name="code"',
            response.text,
        )

    def test_valid_totp_creates_session(self):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
            }
        )

        self.client.cookies.set(
            admin_auth.TOTP_CHALLENGE_COOKIE,
            "challenge-token",
            domain="testserver.local",
            path="/login/totp",
        )

        with (
            patch.object(
                admin_auth.admin_auth_service,
                "verify_totp_challenge",
                return_value=secured_admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_session",
                return_value="session-token",
            ) as create_session,
            patch.object(
                admin_auth.admin_auth_service,
                "create_csrf_token",
                return_value="csrf-token",
            ),
        ):
            response = self.client.post(
                "/login/totp",
                data={
                    "code": "123456",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            303,
        )

        self.assertEqual(
            response.headers["location"],
            "/dashboard",
        )

        create_session.assert_called_once_with(
            secured_admin,
            totp_code="123456",
        )

        self.assertEqual(
            response.cookies.get(
                admin_auth.SESSION_COOKIE
            ),
            "session-token",
        )

    def test_invalid_totp_does_not_create_session(self):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
            }
        )

        self.client.cookies.set(
            admin_auth.TOTP_CHALLENGE_COOKIE,
            "challenge-token",
            domain="testserver.local",
            path="/login/totp",
        )

        with (
            patch.object(
                admin_auth.admin_auth_service,
                "verify_totp_challenge",
                return_value=secured_admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_session",
                side_effect=ValueError(
                    "Additional authentication required."
                ),
            ),
        ):
            response = self.client.post(
                "/login/totp",
                data={
                    "code": "000000",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertIn(
            "Invalid or already used authentication code.",
            response.text,
        )

    def test_totp_page_displays_recovery_code_option(self):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
                "recovery_code_hashes": [
                    "v1$test-recovery-hash",
                ],
            }
        )

        self.client.cookies.set(
            admin_auth.TOTP_CHALLENGE_COOKIE,
            "challenge-token",
            domain="testserver.local",
            path="/login/totp",
        )

        with patch.object(
            admin_auth.admin_auth_service,
            "verify_totp_challenge",
            return_value=secured_admin,
        ):
            response = self.client.get(
                "/login/totp",
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            'action="/login/totp/recovery"',
            response.text,
        )

        self.assertIn(
            'name="recovery_code"',
            response.text,
        )

    def test_valid_recovery_code_creates_session(self):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
                "recovery_code_hashes": [
                    "v1$test-recovery-hash",
                ],
            }
        )

        self.client.cookies.set(
            admin_auth.TOTP_CHALLENGE_COOKIE,
            "challenge-token",
            domain="testserver.local",
            path="/login/totp",
        )

        with (
            patch.object(
                admin_auth.admin_auth_service,
                "verify_totp_challenge",
                return_value=secured_admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_session",
                return_value="session-token",
            ) as create_session,
            patch.object(
                admin_auth.admin_auth_service,
                "create_csrf_token",
                return_value="csrf-token",
            ),
        ):
            response = self.client.post(
                "/login/totp/recovery",
                data={
                    "recovery_code":
                        "  AAAA-BBBB-CCCC-DDDD-EEEE-FFFF  ",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            303,
        )

        self.assertEqual(
            response.headers["location"],
            "/dashboard",
        )

        create_session.assert_called_once_with(
            secured_admin,
            recovery_code=(
                "AAAA-BBBB-CCCC-DDDD-EEEE-FFFF"
            ),
        )

        self.assertEqual(
            response.cookies.get(
                admin_auth.SESSION_COOKIE
            ),
            "session-token",
        )

    def test_invalid_recovery_code_does_not_create_session(
        self,
    ):
        secured_admin = self.admin.model_copy(
            update={
                "totp_enabled": True,
                "totp_secret_encrypted":
                    "encrypted-test-secret",
                "recovery_code_hashes": [
                    "v1$test-recovery-hash",
                ],
            }
        )

        self.client.cookies.set(
            admin_auth.TOTP_CHALLENGE_COOKIE,
            "challenge-token",
            domain="testserver.local",
            path="/login/totp",
        )

        with (
            patch.object(
                admin_auth.admin_auth_service,
                "verify_totp_challenge",
                return_value=secured_admin,
            ),
            patch.object(
                admin_auth.admin_auth_service,
                "create_session",
                side_effect=ValueError(
                    "Additional authentication required."
                ),
            ),
        ):
            response = self.client.post(
                "/login/totp/recovery",
                data={
                    "recovery_code":
                        "AAAA-BBBB-CCCC-DDDD-EEEE-FFFF",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            401,
        )

        self.assertIn(
            "Invalid or already used recovery code.",
            response.text,
        )

        self.assertIn(
            'action="/login/totp/recovery"',
            response.text,
        )

        self.assertIn(
            "<details",
            response.text,
        )

        self.assertIn(
            "open",
            response.text,
        )

    def test_recovery_code_requires_challenge(self):
        with patch.object(
            admin_auth.admin_auth_service,
            "create_session",
        ) as create_session:
            response = self.client.post(
                "/login/totp/recovery",
                data={
                    "recovery_code":
                        "AAAA-BBBB-CCCC-DDDD-EEEE-FFFF",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            303,
        )

        self.assertEqual(
            response.headers["location"],
            "/login",
        )

        create_session.assert_not_called()


if __name__ == "__main__":
    unittest.main()
