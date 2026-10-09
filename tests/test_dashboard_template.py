import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.api import SetupStatus


class DashboardTemplateTests(unittest.TestCase):

    def test_dashboard_template_uses_current_starlette_api(self):
        from app.routers.web.dashboard import (
            dashboard,
        )

        class FakeRequest:
            cookies = {
                "garminsupla_csrf": "test-csrf"
            }

        class FakeUI:
            language = "en"

        class FakeSettings:
            ui = FakeUI()

        with (
            patch(
                "app.routers.web.dashboard.setup_service"
            ) as service,
            patch(
                "app.routers.web.dashboard.resolve_ui_language",
                return_value="en",
            ),
            patch(
                "app.routers.web.dashboard.templates.TemplateResponse"
            ) as render,
        ):
            service.get_status.return_value.setup_completed = True
            service.load_settings.return_value = FakeSettings()

            import asyncio

            asyncio.run(
                dashboard(FakeRequest())
            )

            kwargs = render.call_args.kwargs

            self.assertEqual(
                kwargs["name"],
                "dashboard.html",
            )

            self.assertIn(
                "request",
                kwargs,
            )

            self.assertIn(
                "context",
                kwargs,
            )


if __name__ == "__main__":
    unittest.main()
