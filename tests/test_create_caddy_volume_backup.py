import hashlib
import io
import json
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from scripts.create_caddy_volume_backup import (
    create_caddy_volume_backup,
    read_volume,
)


ROOT_DIR = Path(__file__).resolve().parent.parent


class CaddyVolumeBackupTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        base = Path(temporary.name)

        self.root = base / "installation"
        self.certs = base / "certificates"
        self.backups = base / "backups"

        self.root.mkdir()
        self.certs.mkdir()
        self.backups.mkdir(mode=0o700)

        self.output = (
            self.backups / "volumes.tar.gz"
        )

        self.project = "gstest"

        self.names = (
            "gstest_garminsupla_caddy_data",
            "gstest_garminsupla_caddy_config",
        )

        self.validate_calls = 0
        self.fail_postcheck = False
        self.fail_reader = False
        self.unsafe = None

    def validate(self, project):
        self.assertEqual(
            project,
            self.project,
        )

        self.validate_calls += 1

        if (
            self.fail_postcheck
            and self.validate_calls == 2
        ):
            raise RuntimeError(
                "Volume became active"
            )

        return self.names

    def reader(
        self,
        volume,
        image,
        destination,
    ):
        self.assertIn(volume, self.names)
        self.assertEqual(
            image,
            "sha256:synthetic",
        )

        if self.fail_reader:
            raise RuntimeError(
                "Synthetic reader failed"
            )

        with tarfile.open(
            destination,
            "w",
        ) as archive:

            if self.unsafe:
                item = tarfile.TarInfo(
                    self.unsafe
                )

                if self.unsafe == "symlink":
                    item.type = tarfile.SYMTYPE
                    item.linkname = "/etc/passwd"
                    archive.addfile(item)

                else:
                    item.size = 1
                    archive.addfile(
                        item,
                        io.BytesIO(b"x"),
                    )

                return

            content = (
                f"synthetic:{volume}".encode()
            )

            folder = tarfile.TarInfo(
                "nested/"
            )

            folder.type = tarfile.DIRTYPE
            folder.mode = 0o700

            archive.addfile(folder)

            info = tarfile.TarInfo(
                "nested/value.txt"
            )

            info.size = len(content)
            info.mode = 0o600

            archive.addfile(
                info,
                io.BytesIO(content),
            )

    def create(self):
        with (
            patch(
                "scripts.create_caddy_volume_backup.validate",
                side_effect=self.validate,
            ),
            patch(
                "scripts.create_caddy_volume_backup.read_volume",
                side_effect=self.reader,
            ),
        ):
            create_caddy_volume_backup(
                self.project,
                "sha256:synthetic",
                self.root,
                self.certs,
                self.output,
            )

    def test_integrity_manifest_and_volume_contents(self):
        self.create()

        self.assertEqual(
            self.validate_calls,
            2,
        )

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
                len(archive.getnames()),
                3,
            )

            manifest = json.load(
                archive.extractfile(
                    "manifest.json"
                )
            )

            self.assertEqual(
                manifest["format"],
                "garminsupla-caddy-volumes/v1",
            )

            self.assertFalse(
                manifest["complete_system_backup"]
            )

            self.assertEqual(
                len(manifest["volumes"]),
                2,
            )

            for record in manifest["volumes"]:
                data = archive.extractfile(
                    record["member"]
                ).read()

                self.assertEqual(
                    record["size"],
                    len(data),
                )

                self.assertEqual(
                    record["sha256"],
                    hashlib.sha256(
                        data
                    ).hexdigest(),
                )

                with tarfile.open(
                    fileobj=io.BytesIO(data),
                    mode="r:",
                ) as inner:
                    self.assertEqual(
                        inner.getnames(),
                        [
                            "nested",
                            "nested/value.txt",
                        ],
                    )

                    content = inner.extractfile(
                        "nested/value.txt"
                    ).read()

                    self.assertEqual(
                        content,
                        (
                            f"synthetic:{record['volume']}"
                        ).encode(),
                    )

        self.assertEqual(
            list(self.backups.glob("*.partial")),
            [],
        )

        self.assertEqual(
            list(self.backups.glob("*.tar")),
            [],
        )

    def test_existing_backup_not_overwritten(self):
        self.output.write_bytes(b"original")

        with self.assertRaises(FileExistsError):
            self.create()

        self.assertEqual(
            self.output.read_bytes(),
            b"original",
        )

    def test_rejects_existing_symlink_destination(self):
        self.output.symlink_to(
            self.root
        )

        with self.assertRaises(FileExistsError):
            self.create()

    def test_rejects_world_readable_backup_directory(self):
        self.backups.chmod(0o755)

        with self.assertRaisesRegex(
            ValueError,
            "owner-only",
        ):
            self.create()

    def test_rejects_destination_inside_installation(self):
        self.root.chmod(0o700)

        self.output = (
            self.root / "archive.tar.gz"
        )

        with self.assertRaisesRegex(
            ValueError,
            "outside installation",
        ):
            self.create()

    def test_failed_first_preflight_does_not_publish(self):
        with patch(
            "scripts.create_caddy_volume_backup.validate",
            side_effect=RuntimeError(
                "offline backup refused"
            ),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "offline backup refused",
            ):
                create_caddy_volume_backup(
                    self.project,
                    "sha256:synthetic",
                    self.root,
                    self.certs,
                    self.output,
                )

        self.assertFalse(
            self.output.exists()
        )

    def test_failed_final_preflight_does_not_publish(self):
        self.fail_postcheck = True

        with self.assertRaisesRegex(
            RuntimeError,
            "Volume became active",
        ):
            self.create()

        self.assertFalse(
            self.output.exists()
        )

        self.assertEqual(
            list(self.backups.iterdir()),
            [],
        )

    def test_failed_reader_does_not_publish(self):
        self.fail_reader = True

        with self.assertRaisesRegex(
            RuntimeError,
            "reader failed",
        ):
            self.create()

        self.assertFalse(
            self.output.exists()
        )

        self.assertEqual(
            list(self.backups.iterdir()),
            [],
        )

    def test_symlink_in_volume_archive_is_rejected(self):
        self.unsafe = "symlink"

        with self.assertRaisesRegex(
            ValueError,
            "Unsafe",
        ):
            self.create()

        self.assertFalse(
            self.output.exists()
        )

    def test_path_traversal_in_volume_archive_is_rejected(self):
        self.unsafe = "../escape"

        with self.assertRaisesRegex(
            ValueError,
            "Unsafe",
        ):
            self.create()

        self.assertFalse(
            self.output.exists()
        )

    def test_cli_needs_offline_confirmation(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "scripts.create_caddy_volume_backup",
                "--project",
                self.project,
                "--image",
                "sha256:synthetic",
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

    def test_invalid_image_ref_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "image is required",
        ):
            create_caddy_volume_backup(
                self.project,
                "-fake",
                self.root,
                self.certs,
                self.output,
            )

    def test_reader_docker_flags(self):
        volume = self.names[0]
        inner = self.backups / "volume.tar"

        with patch(
            "scripts.create_caddy_volume_backup.subprocess.run"
        ) as mocked:
            mocked.return_value.returncode = 0

            read_volume(
                volume,
                "sha256:synthetic",
                inner,
            )

            command = mocked.call_args.args[0]

            self.assertEqual(
                command[
                    command.index("--network") + 1
                ],
                "none",
            )

            self.assertIn(
                "--read-only",
                command,
            )

            self.assertEqual(
                command[
                    command.index("--cap-drop") + 1
                ],
                "ALL",
            )

            self.assertEqual(
                command[
                    command.index("--pull") + 1
                ],
                "never",
            )

            self.assertIn(
                (
                    f"type=volume,source={volume},"
                    "target=/source,readonly,volume-nocopy"
                ),
                command,
            )


if __name__ == "__main__":
    unittest.main()
