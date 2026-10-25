import unittest

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


class ComposeMountTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.compose = (
            ROOT_DIR / "docker-compose.example.yml"
        ).read_text(encoding="utf-8")

    def get_service_mounts(self, service):
        lines = self.compose.splitlines()
        marker = f"  {service}:"

        self.assertIn(
            marker,
            lines,
        )

        start = lines.index(marker) + 1

        # Find the end of this service definition.
        # Service fields use four-space indentation.
        end = len(lines)

        for index in range(start, len(lines)):
            line = lines[index]

            if line and not line.startswith("    "):
                end = index
                break

        block = lines[start:end]

        self.assertIn(
            "    volumes:",
            block,
        )

        volume_start = (
            block.index("    volumes:") + 1
        )

        mounts = []

        for line in block[volume_start:]:
            if line.startswith("      - "):
                mounts.append(
                    line.removeprefix(
                        "      - "
                    ).strip()
                )

            elif line.strip():
                break

        return mounts

    def test_admin_service_mounts(self):
        self.assertEqual(
            self.get_service_mounts(
                "garminsupla-api"
            ),
            [
                ".:/app:ro",
                "./data:/app/data:rw",
            ],
        )

    def test_watch_service_mounts(self):
        self.assertEqual(
            self.get_service_mounts(
                "garminsupla-watch"
            ),
            [
                ".:/app:ro",
                "./data:/app/data:rw",
            ],
        )


if __name__ == "__main__":
    unittest.main()
