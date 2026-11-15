import hashlib
import importlib
import io
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from scripts.create_backup import FILES, create_backup


restore_module = importlib.import_module(
    "scripts.restore_file_backup"
)


class RestoreFileBackupTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        self.base = Path(temporary.name)
        self.root = self.base / "installation"
        self.certs = self.base / "certificates"
        self.backups = self.base / "backups"
        self.private = self.base / "private"
        self.archive = self.backups / "source.tar.gz"
        self.target = (
            self.private / "gsrestoreabc12345"
        )

        self.backups.mkdir(mode=0o700)
        self.private.mkdir(mode=0o700)
        self.private.chmod(0o700)

        self.names = list(FILES) + [
            "certs/fullchain.pem",
            "certs/private.key",
            "data/pairing.json",
            "deploy/caddy/secrets/nested/token",
        ]

        for name in self.names:
            path = self.source_path(name)

            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            path.write_bytes(
                b"synthetic:" + name.encode()
            )
            path.chmod(0o600)

        for name in (
            "deploy/caddy/secrets",
            "deploy/caddy/secrets/nested",
        ):
            (self.root / name).chmod(0o700)

        self.build_archive()

    def source_path(self, name):
        if name.startswith("certs/"):
            return self.certs / name.removeprefix(
                "certs/"
            )

        return self.root / name

    def build_archive(self):
        # Only synthetic test fixtures bypass Docker.
        create_backup(
            self.root,
            self.certs,
            self.archive,
            check_offline=False,
        )

    def call_cli(self, confirm):
        command = [
            sys.executable,
            "-B",
            "-m",
            "scripts.restore_file_backup",
            "--archive",
            str(self.archive),
            "--target",
            str(self.target),
        ]

        if confirm:
            command.append("--confirm-isolated")

        return subprocess.run(
            command,
            cwd=Path(__file__).resolve().parent.parent,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_restores_nine_files_and_permissions(self):
        original_hash = hashlib.sha256(
            self.archive.read_bytes()
        ).hexdigest()

        self.assertEqual(
            restore_module.restore_file_backup(
                self.archive,
                self.target,
            ),
            9,
        )

        for name in self.names:
            restored = self.target / name

            self.assertEqual(
                restored.read_bytes(),
                self.source_path(name).read_bytes(),
            )

            self.assertEqual(
                stat.S_IMODE(
                    restored.stat().st_mode
                ),
                0o600,
            )

        for directory in (
            self.target,
            self.target / "data",
            self.target / "certs",
            self.target / "deploy",
            self.target / "deploy/caddy",
            self.target / "deploy/caddy/secrets",
            self.target / "deploy/caddy/secrets/nested",
        ):
            self.assertEqual(
                stat.S_IMODE(
                    directory.stat().st_mode
                ),
                0o700,
            )

        self.assertFalse(
            (self.target / "manifest.json").exists()
        )

        self.assertEqual(
            hashlib.sha256(
                self.archive.read_bytes()
            ).hexdigest(),
            original_hash,
        )

    def test_restores_seven_required_files(self):
        self.source_path(
            "data/pairing.json"
        ).unlink()

        self.source_path(
            "deploy/caddy/secrets/nested/token"
        ).unlink()

        self.archive.unlink()
        self.build_archive()

        self.assertEqual(
            restore_module.restore_file_backup(
                self.archive,
                self.target,
            ),
            7,
        )

        self.assertFalse(
            (self.target / "data/pairing.json").exists()
        )

    def test_existing_target_file_preserved(self):
        self.target.write_bytes(
            b"preserve-existing"
        )

        with self.assertRaises(FileExistsError):
            restore_module.restore_file_backup(
                self.archive,
                self.target,
            )

        self.assertEqual(
            self.target.read_bytes(),
            b"preserve-existing",
        )

    def test_existing_target_directory_preserved(self):
        self.target.mkdir(mode=0o700)

        sentinel = self.target / "sentinel"
        sentinel.write_bytes(
            b"preserve-existing"
        )

        with self.assertRaises(FileExistsError):
            restore_module.restore_file_backup(
                self.archive,
                self.target,
            )

        self.assertEqual(
            sentinel.read_bytes(),
            b"preserve-existing",
        )

    def test_existing_target_symlink_preserved(self):
        self.target.symlink_to(
            self.base / "missing"
        )

        with self.assertRaises(FileExistsError):
            restore_module.restore_file_backup(
                self.archive,
                self.target,
            )

        self.assertTrue(
            self.target.is_symlink()
        )

    def test_wrong_target_name_rejected(self):
        self.target = (
            self.private / "garminsupla"
        )

        with self.assertRaisesRegex(
            ValueError,
            "gsrestore",
        ):
            restore_module.restore_file_backup(
                self.archive,
                self.target,
            )

        self.assertFalse(self.target.exists())

    def test_weak_parent_permissions_rejected(self):
        self.private.chmod(0o755)

        with self.assertRaisesRegex(
            ValueError,
            "0700",
        ):
            restore_module.restore_file_backup(
                self.archive,
                self.target,
            )

        self.assertFalse(self.target.exists())

    def test_source_archive_symlink_rejected(self):
        alias = self.backups / "alias.tar.gz"
        alias.symlink_to(self.archive)

        with self.assertRaisesRegex(
            ValueError,
            "owner-only",
        ):
            restore_module.restore_file_backup(
                alias,
                self.target,
            )

        self.assertFalse(self.target.exists())

    def test_nonprivate_archive_rejected(self):
        self.archive.chmod(0o644)

        with self.assertRaisesRegex(
            ValueError,
            "owner-only",
        ):
            restore_module.restore_file_backup(
                self.archive,
                self.target,
            )

        self.assertFalse(self.target.exists())

    def test_invalid_archive_rejected_before_creation(self):
        self.archive.write_bytes(
            b"not-a-TAR"
        )

        with self.assertRaises(ValueError):
            restore_module.restore_file_backup(
                self.archive,
                self.target,
            )

        self.assertFalse(self.target.exists())

    def test_modified_payload_sha_rejected(self):
        altered = (
            self.backups / "altered.tar.gz"
        )

        with (
            tarfile.open(
                self.archive,
                "r:gz",
            ) as source,
            tarfile.open(
                altered,
                "w:gz",
            ) as output,
        ):
            for member in source:
                payload = source.extractfile(
                    member
                )

                self.assertIsNotNone(payload)
                data = payload.read()

                if member.name == ".env":
                    data = (
                        bytes([data[0] ^ 1])
                        + data[1:]
                    )

                output.addfile(
                    member,
                    io.BytesIO(data),
                )

        altered.chmod(0o600)

        with self.assertRaisesRegex(
            ValueError,
            "SHA-256 or size mismatch",
        ):
            restore_module.restore_file_backup(
                altered,
                self.target,
            )

        self.assertFalse(self.target.exists())

    def test_failure_before_extract_cleans_target(self):
        with patch.object(
            restore_module,
            "_extract",
            side_effect=RuntimeError(
                "synthetic before extract"
            ),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "synthetic before extract",
            ):
                restore_module.restore_file_backup(
                    self.archive,
                    self.target,
                )

        self.assertFalse(self.target.exists())

    def test_failure_after_extract_cleans_target(self):
        original = restore_module._extract

        def failure(*args):
            original(*args)
            raise RuntimeError(
                "synthetic after extract"
            )

        with patch.object(
            restore_module,
            "_extract",
            side_effect=failure,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "synthetic after extract",
            ):
                restore_module.restore_file_backup(
                    self.archive,
                    self.target,
                )

        self.assertFalse(self.target.exists())

    def test_wrong_restored_count_cleans_target(self):
        original = restore_module._extract

        def wrong_count(*args):
            return original(*args) + 1

        with patch.object(
            restore_module,
            "_extract",
            side_effect=wrong_count,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "file count mismatch",
            ):
                restore_module.restore_file_backup(
                    self.archive,
                    self.target,
                )

        self.assertFalse(self.target.exists())

    def test_modified_restored_data_cleans_target(self):
        original_walk = restore_module._walk
        tampered = False

        def change_before_readback(
            root_fd,
            parts,
            directories=None,
        ):
            nonlocal tampered

            if directories is None and not tampered:
                (
                    self.target / "data/admin.json"
                ).write_bytes(
                    b"synthetic altered before readback"
                )

                tampered = True

            return original_walk(
                root_fd,
                parts,
                directories,
            )

        with patch.object(
            restore_module,
            "_walk",
            side_effect=change_before_readback,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "verification failed",
            ):
                restore_module.restore_file_backup(
                    self.archive,
                    self.target,
                )

        self.assertTrue(tampered)
        self.assertFalse(self.target.exists())

    def test_foreign_file_blocks_cleanup_and_is_reported(self):
        original = restore_module._extract

        def foreign_file(*args):
            original(*args)

            (
                self.target / "untracked.txt"
            ).write_bytes(
                b"preserve-foreign"
            )

            raise RuntimeError(
                "synthetic failure"
            )

        with patch.object(
            restore_module,
            "_extract",
            side_effect=foreign_file,
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "cleanup incomplete",
            ):
                restore_module.restore_file_backup(
                    self.archive,
                    self.target,
                )

        self.assertEqual(
            (
                self.target / "untracked.txt"
            ).read_bytes(),
            b"preserve-foreign",
        )

    def test_cli_requires_confirmation(self):
        result = self.call_cli(
            confirm=False
        )

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "--confirm-isolated",
            result.stderr,
        )

        self.assertFalse(self.target.exists())

    def test_cli_success_restores_synthetic_files(self):
        result = self.call_cli(
            confirm=True
        )

        self.assertEqual(
            result.returncode,
            0,
            result.stderr,
        )

        self.assertIn(
            "restored and verified 9 isolated GarminSupla files",
            result.stdout,
        )

        self.assertEqual(
            (
                self.target / "data/admin.json"
            ).read_bytes(),
            b"synthetic:data/admin.json",
        )

        self.assertNotIn(
            "synthetic:",
            result.stdout + result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
