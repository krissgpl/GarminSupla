import unittest

from fastapi.testclient import TestClient

from app.watch_app import watch_app
from app.routers.api import pairing, watch


class WatchAppSurfaceTests(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(
            watch_app,
            base_url="https://testserver",
        )

    def test_only_watch_routers_are_registered(self):
        registered = [
            route.original_router
            for route in watch_app.routes
            if hasattr(route, "original_router")
        ]

        self.assertEqual(len(registered), 2)
        self.assertIs(registered[0], watch.router)
        self.assertIs(registered[1], pairing.router)

    def test_admin_and_web_paths_are_not_exposed(self):
        blocked_paths = (
            "/",
            "/login",
            "/login/totp",
            "/dashboard",
            "/setup",
            "/api/v1/setup/watches",
            "/static/css/style.css",
            "/watch-icons/example.png",
            "/docs",
            "/redoc",
            "/openapi.json",
        )

        for path in blocked_paths:
            with self.subTest(path=path):
                response = self.client.get(
                    path,
                    follow_redirects=False,
                )

                self.assertEqual(
                    response.status_code,
                    404,
                )

    def test_watch_endpoint_is_registered(self):
        routes = [
            route
            for included in watch_app.routes
            if hasattr(included, "original_router")
            for route in included.original_router.routes
        ]

        paths = {
            f"/api/v1{route.path}"
            for route in routes
        }

        self.assertIn(
            "/api/v1/watch/me",
            paths,
        )

        self.assertIn(
            "/api/v1/watch/pair",
            paths,
        )


if __name__ == "__main__":
    unittest.main()
