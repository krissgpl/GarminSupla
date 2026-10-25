import subprocess
import sys
import tempfile
import unittest

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


class InitDeployTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.target = Path(self.temp_dir.name)

        self.compose = (
            self.target / "docker-compose.yml"
        )

        self.caddy = (
            self.target / "deploy/caddy/Caddyfile"
        )

    def run_init(self):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.init_deploy",
                "--target-dir",
                str(self.target),
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=True,
        )

    def test_creates_deployment_files(self):
        self.run_init()

        self.assertEqual(
            self.compose.read_bytes(),
            (
                ROOT_DIR / "docker-compose.example.yml"
            ).read_bytes(),
        )

        self.assertEqual(
            self.caddy.read_bytes(),
            (
                ROOT_DIR / "deploy/caddy/Caddyfile.example"
            ).read_bytes(),
        )

    def test_existing_files_are_preserved(self):
        self.run_init()

        self.compose.write_text(
            "production-compose",
            encoding="utf-8",
        )

        self.caddy.write_text(
            "production-caddy",
            encoding="utf-8",
        )

        self.run_init()

        self.assertEqual(
            self.compose.read_text(
                encoding="utf-8"
            ),
            "production-compose",
        )

        self.assertEqual(
            self.caddy.read_text(
                encoding="utf-8"
            ),
            "production-caddy",
        )

    def test_existing_compose_is_preserved(self):
        self.compose.write_text(
            "existing-compose",
            encoding="utf-8",
        )

        self.run_init()

        self.assertEqual(
            self.compose.read_text(
                encoding="utf-8"
            ),
            "existing-compose",
        )

        self.assertTrue(
            self.caddy.is_file()
        )

    def test_existing_caddy_is_preserved(self):
        self.caddy.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.caddy.write_text(
            "existing-caddy",
            encoding="utf-8",
        )

        self.run_init()

        self.assertEqual(
            self.caddy.read_text(
                encoding="utf-8"
            ),
            "existing-caddy",
        )

        self.assertTrue(
            self.compose.is_file()
        )

    def test_existing_symlink_is_preserved(self):
        original = self.target / "original.txt"

        original.write_text(
            "keep-original",
            encoding="utf-8",
        )

        self.compose.symlink_to(original)

        self.run_init()

        self.assertTrue(
            self.compose.is_symlink()
        )

        self.assertEqual(
            original.read_text(
                encoding="utf-8"
            ),
            "keep-original",
        )


if __name__ == "__main__":
    unittest.main()
