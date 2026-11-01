import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent

OVERRIDE = (
    ROOT_DIR / "docker-compose.nonroot.example.yml"
)

USER_SETTING = (
    '    user: "${GARMIN_SUPLA_RUN_UID:-1000}:'
    '${GARMIN_SUPLA_RUN_GID:-1000}"'
)


class ComposeNonrootTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.content = OVERRIDE.read_text(
            encoding="utf-8"
        )

    def test_both_application_services_use_nonroot(self):
        for service in (
            "garminsupla-api",
            "garminsupla-watch",
        ):
            with self.subTest(service=service):
                self.assertIn(
                    f"  {service}:\n"
                    f"{USER_SETTING}",
                    self.content,
                )

        self.assertEqual(
            self.content.count(USER_SETTING),
            2,
        )

    def test_proxy_is_not_modified(self):
        self.assertNotIn(
            "garminsupla-watch-proxy:",
            self.content,
        )

    def test_override_does_not_change_mounts_or_ports(self):
        for forbidden in (
            "    volumes:",
            "    ports:",
            "    build:",
            "    image:",
            "    command:",
        ):
            with self.subTest(field=forbidden):
                self.assertNotIn(
                    forbidden,
                    self.content,
                )


if __name__ == "__main__":
    unittest.main()
