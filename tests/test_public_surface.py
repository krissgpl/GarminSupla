import unittest

from fastapi.testclient import TestClient

from app.main import app


class PublicSurfaceTests(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(
            app,
            base_url="https://testserver",
        )

    def test_api_documentation_is_disabled(self):
        for path in (
            "/docs",
            "/redoc",
            "/openapi.json",
        ):
            with self.subTest(path=path):
                response = self.client.get(
                    path,
                    follow_redirects=False,
                )

                self.assertEqual(
                    response.status_code,
                    404,
                )


if __name__ == "__main__":
    unittest.main()
