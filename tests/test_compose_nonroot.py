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

MOUNT_SECTION = (
    "    volumes:\n"
    "      - .:/app:ro\n"
    "      - ./data:/app/data:rw"
)


class ComposeNonrootTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.content = OVERRIDE.read_text(
            encoding="utf-8"
        )

    def test_both_services_use_nonroot(self):
        for service in (
            "garminsupla-api",
            "garminsupla-watch",
        ):
            with self.subTest(service=service):
                self.assertIn(
                    f"  {service}:\n"
                    f"{USER_SETTING}\n"
                    f"{MOUNT_SECTION}",
                    self.content,
                )

        self.assertEqual(
            self.content.count(USER_SETTING),
            2,
        )

    def test_both_services_protect_code_and_data(self):
        self.assertEqual(
            self.content.count(
                "      - .:/app:ro"
            ),
            2,
        )

        self.assertEqual(
            self.content.count(
                "      - ./data:/app/data:rw"
            ),
            2,
        )

        self.assertNotIn(
            "      - .:/app\n",
            self.content,
        )

    def test_proxy_and_ports_are_unchanged(self):
        for forbidden in (
            "garminsupla-watch-proxy:",
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
