import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from app.config import AppSettings


ROOT_DIR = Path(__file__).resolve().parent.parent


class InitEnvTests(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.directory = Path(self.temp_dir.name)
        self.target = self.directory / ".env"

    def run_init(self, target=None):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.init_env",
                "--output",
                str(
                    target
                    if target is not None
                    else self.target
                ),
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            check=True,
        )

    def get_secret(self, path):
        lines = path.read_text(
            encoding="utf-8"
        ).splitlines()

        values = [
            line.split("=", 1)[1]
            for line in lines
            if line.startswith(
                "ADMIN_SESSION_SECRET="
            )
        ]

        self.assertEqual(len(values), 1)

        return values[0]

    def test_creates_strong_session_secret(self):
        result = self.run_init()

        self.assertTrue(self.target.is_file())

        secret = self.get_secret(self.target)

        self.assertRegex(
            secret,
            r"^[A-Za-z0-9_-]{60,}$",
        )

        self.assertIn(
            "APP_NAME=GarminSupla",
            self.target.read_text(
                encoding="utf-8"
            ),
        )

        self.assertNotIn(
            secret,
            result.stdout,
        )

    @unittest.skipUnless(
        os.name == "posix",
        "POSIX file permissions required",
    )
    def test_file_permissions_are_private(self):
        self.run_init()

        mode = stat.S_IMODE(
            self.target.stat().st_mode
        )

        self.assertEqual(
            mode,
            0o600,
        )

    def test_existing_configuration_is_preserved(self):
        original = (
            "APP_NAME=ExistingInstallation\n"
            "ADMIN_SESSION_SECRET=keep-this-secret\n"
            "CUSTOM_SETTING=keep-this-value\n"
        )

        self.target.write_text(
            original,
            encoding="utf-8",
        )

        result = self.run_init()

        self.assertEqual(
            self.target.read_text(
                encoding="utf-8"
            ),
            original,
        )

        self.assertIn(
            "preserved",
            result.stdout,
        )

    def test_generates_unique_secrets(self):
        first = self.directory / "first.env"
        second = self.directory / "second.env"

        self.run_init(first)
        self.run_init(second)

        self.assertNotEqual(
            self.get_secret(first),
            self.get_secret(second),
        )

    def test_generated_env_loads_without_oauth_settings(self):
        self.run_init()

        with patch.dict(
            os.environ,
            {},
            clear=True,
        ):
            config = AppSettings(
                _env_file=self.target,
            )

        self.assertEqual(
            config.admin_session_secret,
            self.get_secret(self.target),
        )

        self.assertIsNone(
            config.supla_client_id
        )
        self.assertIsNone(
            config.supla_client_secret
        )
        self.assertIsNone(
            config.supla_redirect_uri
        )

        self.assertIn(
            "offline_access",
            config.supla_scope.split(),
        )

    @unittest.skipUnless(
        os.name == "posix",
        "Symbolic-link test requires POSIX",
    )
    def test_existing_symlink_is_not_overwritten(self):
        original = self.directory / "original.txt"

        original.write_text(
            "preserve-this-file",
            encoding="utf-8",
        )

        self.target.symlink_to(original)

        self.run_init()

        self.assertTrue(self.target.is_symlink())

        self.assertEqual(
            original.read_text(
                encoding="utf-8"
            ),
            "preserve-this-file",
        )


if __name__ == "__main__":
    unittest.main()
