import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


class CheckBackupTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        self.root = (
            Path(temporary.name) / "installation"
        )

        self.certs = (
            Path(temporary.name) / "certificates"
        )

        (self.root / "deploy/caddy").mkdir(
            parents=True
        )

        (self.root / "data").mkdir()
        self.certs.mkdir()

        for name in (
            ".env",
            "docker-compose.yml",
            "deploy/caddy/Caddyfile",
            "data/config.json",
            "data/admin.json",
        ):
            path = self.root / name

            path.write_text(
                "sample-secret-do-not-print",
                encoding="utf-8",
            )

            path.chmod(0o600)

        for name in (
            "fullchain.pem",
            "private.key",
        ):
            path = self.certs / name

            path.write_text(
                "sample-secret-do-not-print",
                encoding="utf-8",
            )

            path.chmod(0o600)

    def run_preflight(
        self,
        cert_dir=None,
    ):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.check_backup",
                "--root",
                str(self.root),
                "--cert-dir",
                str(
                    cert_dir
                    if cert_dir is not None
                    else self.certs
                ),
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def test_complete_private_fixture_passes_without_disclosing_contents(
        self,
    ):
        result = self.run_preflight()

        self.assertEqual(
            result.returncode,
            0,
            result.stdout + result.stderr,
        )

        self.assertIn(
            "no backup created",
            result.stdout,
        )

        self.assertNotIn(
            "sample-secret-do-not-print",
            result.stdout + result.stderr,
        )

        self.assertFalse(
            any(self.root.glob("*.tar*"))
        )

    def test_missing_admin_configuration_fails(self):
        (
            self.root / "data/admin.json"
        ).unlink()

        result = self.run_preflight()

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "data/admin.json",
            result.stdout,
        )

    def test_world_readable_env_fails(self):
        (
            self.root / ".env"
        ).chmod(0o644)

        result = self.run_preflight()

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "insecure permissions 0644",
            result.stdout,
        )

    def test_historical_config_copy_with_weak_permissions_fails(
        self,
    ):
        history = (
            self.root
            / "data/config.json.before-watch-items"
        )

        history.write_text(
            "old-sensitive-data",
            encoding="utf-8",
        )

        history.chmod(0o644)

        result = self.run_preflight()

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "data/config.json.before-watch-items",
            result.stdout,
        )

        self.assertNotIn(
            "old-sensitive-data",
            result.stdout,
        )

    def test_symlink_instead_of_secret_fails(self):
        secret = self.root / ".env"

        secret.unlink()

        secret.symlink_to(
            self.root / "data/config.json"
        )

        result = self.run_preflight()

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "not a link",
            result.stdout,
        )

    def test_relative_cert_path_fails(self):
        result = self.run_preflight(
            cert_dir=Path("relative/certificates")
        )

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "absolute",
            result.stdout,
        )

    def test_optional_pairing_file_with_private_permissions_passes(
        self,
    ):
        pairing = (
            self.root / "data/pairing.json"
        )

        pairing.write_text(
            "temporary-pairing",
            encoding="utf-8",
        )

        pairing.chmod(0o600)

        self.assertEqual(
            self.run_preflight().returncode,
            0,
        )

    def test_weak_pairing_permissions_fails(self):
        pairing = (
            self.root / "data/pairing.json"
        )

        pairing.write_text(
            "temporary-pairing",
            encoding="utf-8",
        )

        pairing.chmod(0o644)

        self.assertNotEqual(
            self.run_preflight().returncode,
            0,
        )


if __name__ == "__main__":
    unittest.main()
