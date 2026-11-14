import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest

from pathlib import Path

from scripts.create_backup import FILES
from scripts.verify_file_backup import (
    MAX_MANIFEST,
    verify_archive,
)


ROOT = Path(__file__).resolve().parent.parent

REQUIRED = set(FILES) | {
    "certs/fullchain.pem",
    "certs/private.key",
}

OPTIONAL = {
    "data/pairing.json",
    "deploy/caddy/secrets/nested/token",
}

EXCLUDES = [
    "caddy_docker_volumes",
    "historical_data_copies",
    "lock_files",
]


class VerifyFileBackupTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name)
        self.archive = (
            self.directory / "backup.tar.gz"
        )

        self.entries = [
            (
                name,
                b"synthetic:" + name.encode(),
            )
            for name in sorted(
                REQUIRED | OPTIONAL
            )
        ]

        self.write_archive()

    @staticmethod
    def make_manifest(entries):
        return {
            "format": "garminsupla-files/v1",
            "complete_system_backup": False,
            "excludes": list(EXCLUDES),
            "files": [
                {
                    "path": name,
                    "size": len(data),
                    "sha256": hashlib.sha256(
                        data
                    ).hexdigest(),
                }
                for name, data in entries
            ],
        }

    def write_archive(
        self,
        *,
        entries=None,
        manifest=None,
        manifest_raw=None,
        include_manifest=True,
        overrides=None,
    ):
        if entries is None:
            entries = list(self.entries)

        if manifest is None:
            manifest = self.make_manifest(
                entries
            )

        if manifest_raw is None:
            manifest_raw = json.dumps(
                manifest
            ).encode("utf-8")

        overrides = overrides or {}

        with tarfile.open(
            self.archive,
            mode="w:gz",
        ) as archive:

            for name, data in entries:
                options = overrides.get(
                    name,
                    {},
                )

                member = tarfile.TarInfo(
                    name
                )

                member.mode = options.get(
                    "mode",
                    0o600,
                )

                member.uid = options.get(
                    "uid",
                    0,
                )

                member.gid = options.get(
                    "gid",
                    0,
                )

                member.type = options.get(
                    "type",
                    tarfile.REGTYPE,
                )

                if member.isfile():
                    member.size = len(data)

                    archive.addfile(
                        member,
                        io.BytesIO(data),
                    )
                else:
                    member.linkname = options.get(
                        "linkname",
                        ".env",
                    )

                    archive.addfile(member)

            if include_manifest:
                item = tarfile.TarInfo(
                    "manifest.json"
                )

                item.size = len(
                    manifest_raw
                )
                item.mode = 0o600
                item.uid = 0
                item.gid = 0

                archive.addfile(
                    item,
                    io.BytesIO(
                        manifest_raw
                    ),
                )

        self.archive.chmod(0o600)

    def test_valid_archive_with_optional_files(self):
        self.assertEqual(
            verify_archive(
                self.archive
            ),
            9,
        )

    def test_valid_archive_without_optional_files(self):
        entries = [
            entry
            for entry in self.entries
            if entry[0] in REQUIRED
        ]

        self.write_archive(
            entries=entries
        )

        self.assertEqual(
            verify_archive(
                self.archive
            ),
            7,
        )

    def test_missing_required_file_rejected(self):
        entries = [
            entry
            for entry in self.entries
            if entry[0] != "data/admin.json"
        ]

        self.write_archive(
            entries=entries
        )

        with self.assertRaisesRegex(
            ValueError,
            "Required backup files",
        ):
            verify_archive(
                self.archive
            )

    def test_modified_payload_sha_rejected(self):
        manifest = self.make_manifest(
            self.entries
        )

        entries = [
            (
                name,
                b"altered" if name == ".env"
                else data,
            )
            for name, data in self.entries
        ]

        self.write_archive(
            entries=entries,
            manifest=manifest,
        )

        with self.assertRaisesRegex(
            ValueError,
            "SHA-256 or size mismatch",
        ):
            verify_archive(
                self.archive
            )

    def test_modified_manifest_size_rejected(self):
        manifest = self.make_manifest(
            self.entries
        )

        manifest["files"][0]["size"] += 1

        self.write_archive(
            manifest=manifest
        )

        with self.assertRaisesRegex(
            ValueError,
            "SHA-256 or size mismatch",
        ):
            verify_archive(
                self.archive
            )

    def test_unexpected_archive_path_rejected(self):
        entries = self.entries + [
            (
                "data/unexpected.json",
                b"synthetic",
            )
        ]

        self.write_archive(
            entries=entries
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unexpected backup archive path",
        ):
            verify_archive(
                self.archive
            )

    def test_secret_path_traversal_rejected(self):
        entries = self.entries + [
            (
                "deploy/caddy/secrets/../escape",
                b"synthetic",
            )
        ]

        self.write_archive(
            entries=entries
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unexpected backup archive path",
        ):
            verify_archive(
                self.archive
            )

    def test_duplicate_tar_entry_rejected(self):
        entries = self.entries + [
            self.entries[0]
        ]

        self.write_archive(
            entries=entries
        )

        with self.assertRaisesRegex(
            ValueError,
            "Duplicate backup archive entry",
        ):
            verify_archive(
                self.archive
            )

    def test_tar_symlink_rejected(self):
        self.write_archive(
            overrides={
                ".env": {
                    "type": tarfile.SYMTYPE,
                    "linkname": "data/admin.json",
                },
            },
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsafe backup archive entry metadata",
        ):
            verify_archive(
                self.archive
            )

    def test_world_readable_tar_member_rejected(self):
        self.write_archive(
            overrides={
                ".env": {
                    "mode": 0o644,
                },
            },
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsafe backup archive entry metadata",
        ):
            verify_archive(
                self.archive
            )

    def test_wrong_tar_owner_rejected(self):
        self.write_archive(
            overrides={
                ".env": {
                    "uid": 1000,
                },
            },
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsafe backup archive entry metadata",
        ):
            verify_archive(
                self.archive
            )

    def test_missing_manifest_rejected(self):
        self.write_archive(
            include_manifest=False
        )

        with self.assertRaisesRegex(
            ValueError,
            "Missing or invalid backup manifest",
        ):
            verify_archive(
                self.archive
            )

    def test_invalid_json_manifest_rejected(self):
        self.write_archive(
            manifest_raw=b"{invalid-json",
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid GarminSupla file backup archive",
        ):
            verify_archive(
                self.archive
            )

    def test_wrong_format_rejected(self):
        manifest = self.make_manifest(
            self.entries
        )

        manifest["format"] = (
            "unknown-format"
        )

        self.write_archive(
            manifest=manifest
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid file backup manifest",
        ):
            verify_archive(
                self.archive
            )

    def test_complete_system_flag_rejected(self):
        manifest = self.make_manifest(
            self.entries
        )

        manifest[
            "complete_system_backup"
        ] = True

        self.write_archive(
            manifest=manifest
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid file backup manifest",
        ):
            verify_archive(
                self.archive
            )

    def test_changed_exclusions_rejected(self):
        manifest = self.make_manifest(
            self.entries
        )

        manifest["excludes"] = []

        self.write_archive(
            manifest=manifest
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid file backup manifest",
        ):
            verify_archive(
                self.archive
            )

    def test_duplicate_manifest_record_rejected(self):
        manifest = self.make_manifest(
            self.entries
        )

        manifest["files"][-1] = dict(
            manifest["files"][0]
        )

        self.write_archive(
            manifest=manifest
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid backup file manifest record",
        ):
            verify_archive(
                self.archive
            )

    def test_boolean_manifest_size_rejected(self):
        manifest = self.make_manifest(
            self.entries
        )

        manifest["files"][0]["size"] = True

        self.write_archive(
            manifest=manifest
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid backup file manifest record",
        ):
            verify_archive(
                self.archive
            )

    def test_invalid_manifest_sha_rejected(self):
        manifest = self.make_manifest(
            self.entries
        )

        manifest["files"][0]["sha256"] = (
            "not-a-valid-sha256"
        )

        self.write_archive(
            manifest=manifest
        )

        with self.assertRaisesRegex(
            ValueError,
            "Invalid backup file manifest record",
        ):
            verify_archive(
                self.archive
            )

    def test_nonprivate_archive_rejected(self):
        self.archive.chmod(0o644)

        with self.assertRaisesRegex(
            ValueError,
            "owner-only",
        ):
            verify_archive(
                self.archive
            )

    def test_archive_symlink_rejected(self):
        alias = (
            self.directory / "alias.tar.gz"
        )

        alias.symlink_to(
            self.archive
        )

        with self.assertRaisesRegex(
            ValueError,
            "regular owner-only",
        ):
            verify_archive(
                alias
            )

    def test_oversized_manifest_rejected(self):
        self.write_archive(
            manifest_raw=(
                b" " * (MAX_MANIFEST + 1)
            ),
        )

        with self.assertRaisesRegex(
            ValueError,
            "Oversized backup manifest",
        ):
            verify_archive(
                self.archive
            )

    def test_cli_success_is_read_only(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "scripts.verify_file_backup",
                "--archive",
                str(self.archive),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(
            result.returncode,
            0,
            result.stderr,
        )

        self.assertIn(
            "verified 9 GarminSupla backup files",
            result.stdout,
        )

        self.assertIn(
            "no files restored",
            result.stdout,
        )

        self.assertNotIn(
            "synthetic:",
            result.stdout + result.stderr,
        )

    def test_cli_failure_is_reported(self):
        self.archive.chmod(0o644)

        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "scripts.verify_file_backup",
                "--archive",
                str(self.archive),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "ERROR:",
            result.stderr,
        )

        self.assertNotIn(
            "synthetic:",
            result.stdout + result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
