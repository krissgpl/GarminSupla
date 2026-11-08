import json
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from scripts.create_backup import (
    create_backup,
    check_services_stopped,
)


ROOT_DIR = Path(__file__).resolve().parent.parent


class CreateBackupTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        base = Path(temporary.name)

        self.root = base / "installation"
        self.certs = base / "certs"
        self.output_dir = base / "backups"

        (self.root / "data").mkdir(
            parents=True
        )

        secrets = (
            self.root / "deploy/caddy/secrets"
        )

        secrets.mkdir(parents=True)
        secrets.chmod(0o700)

        self.certs.mkdir()
        self.output_dir.mkdir(mode=0o700)

        self.output = (
            self.output_dir / "backup.tar.gz"
        )

        self.file_map = {
            ".env": self.root / ".env",
            "docker-compose.yml":
                self.root / "docker-compose.yml",
            "deploy/caddy/Caddyfile":
                self.root / "deploy/caddy/Caddyfile",
            "data/config.json":
                self.root / "data/config.json",
            "data/admin.json":
                self.root / "data/admin.json",
            "certs/fullchain.pem":
                self.certs / "fullchain.pem",
            "certs/private.key":
                self.certs / "private.key",
        }

        for name, path in self.file_map.items():
            path.write_bytes(
                ("private-fixture:" + name).encode()
            )
            path.chmod(0o600)

    def create(self):
        # Only unit fixtures bypass the Docker check.
        create_backup(
            self.root,
            self.certs,
            self.output,
            check_offline=False,
        )

    def test_archive_contains_files_and_manifest(self):
        self.create()

        self.assertEqual(
            stat.S_IMODE(
                self.output.stat().st_mode
            ),
            0o600,
        )

        with tarfile.open(
            self.output,
            "r:gz",
        ) as archive:
            self.assertEqual(
                set(archive.getnames()),
                set(self.file_map)
                | {"manifest.json"},
            )

            for name, path in self.file_map.items():
                self.assertEqual(
                    archive.extractfile(name).read(),
                    path.read_bytes(),
                )

                self.assertEqual(
                    archive.getmember(name).mode,
                    0o600,
                )

            manifest = json.load(
                archive.extractfile(
                    "manifest.json"
                )
            )

            self.assertEqual(
                manifest["format"],
                "garminsupla-files/v1",
            )

            self.assertFalse(
                manifest["complete_system_backup"]
            )

            self.assertIn(
                "caddy_docker_volumes",
                manifest["excludes"],
            )

    def test_does_not_overwrite_existing_backup(self):
        self.output.write_bytes(
            b"preserve-existing"
        )

        with self.assertRaises(FileExistsError):
            self.create()

        self.assertEqual(
            self.output.read_bytes(),
            b"preserve-existing",
        )

    def test_rejects_nonprivate_output_directory(self):
        self.output_dir.chmod(0o755)

        with self.assertRaisesRegex(
            ValueError,
            "owner-only",
        ):
            self.create()

        self.assertFalse(self.output.exists())

    def test_rejects_output_inside_source_root(self):
        (self.root / "data").chmod(0o700)

        self.output = (
            self.root / "data/snapshot.tar.gz"
        )

        with self.assertRaisesRegex(
            ValueError,
            "outside installation",
        ):
            self.create()

        self.assertFalse(self.output.exists())

    def test_includes_pairing_and_caddy_secrets(self):
        pairing = (
            self.root / "data/pairing.json"
        )

        pairing.write_text(
            "temporary",
            encoding="utf-8",
        )
        pairing.chmod(0o600)

        secret = (
            self.root
            / "deploy/caddy/secrets/token"
        )

        secret.write_text(
            "caddy-token",
            encoding="utf-8",
        )
        secret.chmod(0o600)

        self.create()

        with tarfile.open(
            self.output,
            "r:gz",
        ) as archive:
            self.assertEqual(
                archive.extractfile(
                    "data/pairing.json"
                ).read(),
                b"temporary",
            )

            self.assertEqual(
                archive.extractfile(
                    "deploy/caddy/secrets/token"
                ).read(),
                b"caddy-token",
            )

    def test_rejects_weak_caddy_secret_permissions(self):
        secret = (
            self.root
            / "deploy/caddy/secrets/token"
        )

        secret.write_text(
            "caddy-token",
            encoding="utf-8",
        )

        secret.chmod(0o644)

        with self.assertRaisesRegex(
            ValueError,
            "unsafe",
        ):
            self.create()

        self.assertFalse(self.output.exists())

    def test_rejects_caddy_secret_symlink(self):
        secret = (
            self.root
            / "deploy/caddy/secrets/token"
        )

        secret.symlink_to(
            self.root / ".env"
        )

        with self.assertRaisesRegex(
            ValueError,
            "unsafe",
        ):
            self.create()

        self.assertFalse(self.output.exists())

    def test_cli_requires_offline_confirmation(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "scripts.create_backup",
                "--root",
                str(self.root),
                "--cert-dir",
                str(self.certs),
                "--output",
                str(self.output),
            ],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "--confirm-stopped",
            result.stderr,
        )

        self.assertFalse(self.output.exists())

    def test_refuses_running_docker_services(self):
        with patch(
            "scripts.create_backup.subprocess.run"
        ) as mocked:
            mocked.return_value.returncode = 0
            mocked.return_value.stdout = (
                "running-container-id\n"
            )

            with self.assertRaisesRegex(
                RuntimeError,
                "running",
            ):
                check_services_stopped(
                    self.root
                )

    def test_docker_error_fails_closed(self):
        with patch(
            "scripts.create_backup.subprocess.run"
        ) as mocked:
            mocked.return_value.returncode = 1
            mocked.return_value.stdout = ""

            with self.assertRaisesRegex(
                RuntimeError,
                "could not be verified",
            ):
                check_services_stopped(
                    self.root
                )


if __name__ == "__main__":
    unittest.main()
