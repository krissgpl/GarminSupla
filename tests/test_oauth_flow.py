import unittest

from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.admin_auth import require_admin_web
from app.core.exception_handlers import (
    register_exception_handlers,
)
from app.models.admin import AdminAccount
from app.routers.web import oauth


class OAuthFlowTests(unittest.TestCase):

    def setUp(self):
        self.app = FastAPI()

        register_exception_handlers(
            self.app
        )

        self.app.include_router(
            oauth.router
        )

        self.client = TestClient(
            self.app,
            base_url="https://testserver",
        )

        self.admin = AdminAccount(
            username="test-admin",
            password_hash="test-password-hash",
            created_at="2026-10-03T00:00:00+00:00",
        )

    def _authenticate_admin(self):
        self.app.dependency_overrides[
            require_admin_web
        ] = lambda: self.admin

        self.addCleanup(
            self.app.dependency_overrides.clear
        )

    def test_callback_rejects_invalid_state(self):
        self._authenticate_admin()

        self.client.cookies.set(
            oauth.OAUTH_STATE_COOKIE,
            "expected-state",
            domain="testserver.local",
            path="/oauth",
        )

        with patch.object(
            oauth.oauth_service,
            "complete_authorization",
        ) as complete_authorization:
            response = self.client.get(
                "/oauth/callback",
                params={
                    "code": "authorization-code",
                    "state": "invalid-state",
                },
                follow_redirects=False,
            )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertEqual(
            response.json(),
            {
                "detail": "Invalid OAuth state.",
            },
        )

        complete_authorization.assert_not_called()

    def test_callback_requires_authenticated_admin(self):
        self.client.cookies.set(
            oauth.OAUTH_STATE_COOKIE,
            "expected-state",
            domain="testserver.local",
            path="/oauth",
        )

        with patch.object(
            oauth.oauth_service,
            "complete_authorization",
        ) as complete_authorization:
            response = self.client.get(
                "/oauth/callback",
                params={
                    "code": "authorization-code",
                    "state": "expected-state",
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

        complete_authorization.assert_not_called()


if __name__ == "__main__":
    unittest.main()
