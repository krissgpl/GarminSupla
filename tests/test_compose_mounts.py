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


    def test_new_install_uses_nonroot(self):
        user_line = (
            '    user: "${GARMIN_SUPLA_RUN_UID:-1000}:'
            '${GARMIN_SUPLA_RUN_GID:-1000}"'
        )

        for service in (
            "garminsupla-api",
            "garminsupla-watch",
        ):
            with self.subTest(service=service):
                self.assertIn(
                    f"  {service}:\n"
                    f"    build: .\n"
                    f"{user_line}\n",
                    self.compose,
                )

        self.assertEqual(
            self.compose.count(user_line),
            2,
        )


    def test_caddy_waits_for_watch_health(self):
        self.assertIn(
            "    healthcheck:\n"
            "      test:\n"
            "        - CMD\n"
            "        - python\n"
            "        - -c\n",
            self.compose,
        )

        self.assertIn(
            "socket.create_connection",
            self.compose,
        )

        self.assertIn(
            "    depends_on:\n"
            "      garminsupla-watch:\n"
            "        condition: service_healthy\n",
            self.compose,
        )


    def test_caddy_disallows_new_privileges(self):
        proxy = self.compose.split(
            "  garminsupla-watch-proxy:\n",
            1,
        )[1].split("\nvolumes:\n", 1)[0]

        self.assertIn(
            "    security_opt:\n"
            "      - no-new-privileges:true\n",
            proxy,
        )


    def test_caddy_root_filesystem_is_read_only(self):
        proxy = self.compose.split(
            "  garminsupla-watch-proxy:\n",
            1,
        )[1].split("\nvolumes:\n", 1)[0]

        self.assertIn(
            "    read_only: true\n",
            proxy,
        )

        self.assertIn(
            "      - garminsupla_caddy_data:/data\n",
            proxy,
        )

        self.assertIn(
            "      - garminsupla_caddy_config:/config\n",
            proxy,
        )


    def test_python_services_disallow_new_privileges(self):
        for service in (
            "garminsupla-api",
            "garminsupla-watch",
        ):
            with self.subTest(service=service):
                block = self.compose.split(
                    f"  {service}:\n",
                    1,
                )[1].split("\n  garminsupla-", 1)[0]

                self.assertIn(
                    "    security_opt:\n"
                    "      - no-new-privileges:true\n",
                    block,
                )


    def test_watch_drops_all_linux_capabilities(self):
        watch = self.compose.split(
            "  garminsupla-watch:\n",
            1,
        )[1].split(
            "\n  garminsupla-watch-proxy:",
            1,
        )[0]

        self.assertIn(
            "    cap_drop:\n"
            "      - ALL\n",
            watch,
        )

        self.assertIn(
            "    security_opt:\n"
            "      - no-new-privileges:true\n",
            watch,
        )


    def test_admin_api_drops_all_linux_capabilities(self):
        admin = self.compose.split(
            "  garminsupla-api:\n",
            1,
        )[1].split(
            "\n  garminsupla-watch:",
            1,
        )[0]

        self.assertIn(
            "    cap_drop:\n"
            "      - ALL\n",
            admin,
        )

        self.assertIn(
            "    security_opt:\n"
            "      - no-new-privileges:true\n",
            admin,
        )


    def test_watch_root_filesystem_is_read_only(self):
        watch = self.compose.split(
            "  garminsupla-watch:\n",
            1,
        )[1].split(
            "\n  garminsupla-watch-proxy:",
            1,
        )[0]

        self.assertIn(
            "    read_only: true\n",
            watch,
        )

        self.assertIn(
            "      - .:/app:ro\n",
            watch,
        )

        self.assertIn(
            "      - ./data:/app/data:rw\n",
            watch,
        )


    def test_admin_root_filesystem_is_read_only(self):
        admin = self.compose.split(
            "  garminsupla-api:\n",
            1,
        )[1].split(
            "\n  garminsupla-watch:",
            1,
        )[0]

        self.assertIn(
            "    read_only: true\n",
            admin,
        )

        self.assertIn(
            "      - .:/app:ro\n",
            admin,
        )

        self.assertIn(
            "      - ./data:/app/data:rw\n",
            admin,
        )


    def test_admin_api_has_healthcheck(self):
        admin = self.compose.split(
            "  garminsupla-api:\n",
            1,
        )[1].split(
            "\n  garminsupla-watch:",
            1,
        )[0]

        expected = (
            "    healthcheck:\n"
            "      test:\n"
            "        - CMD\n"
            "        - python\n"
            "        - -c\n"
            '        - "import socket; socket.create_connection('
            "('127.0.0.1', 8008), timeout=2).close()"
            '"\n'
            "      interval: 5s\n"
            "      timeout: 3s\n"
            "      retries: 12\n"
            "      start_period: 10s\n"
        )

        self.assertIn(expected, admin)


    def test_watch_api_has_pid_limit(self):
        watch = self.compose.split(
            "  garminsupla-watch:\n",
            1,
        )[1].split(
            "\n  garminsupla-watch-proxy:",
            1,
        )[0]

        self.assertIn(
            "    pids_limit: 256\n",
            watch,
        )

        admin = self.compose.split(
            "  garminsupla-api:\n",
            1,
        )[1].split(
            "\n  garminsupla-watch:",
            1,
        )[0]

        self.assertNotIn(
            "    pids_limit:",
            admin,
        )


if __name__ == "__main__":
    unittest.main()
