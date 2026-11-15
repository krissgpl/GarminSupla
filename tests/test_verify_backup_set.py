"""Manifest and filesystem safety tests for the backup-set verifier.

The two archive parsers have their own tests; these tests deliberately
mock only those parsers, never the outer manifest/hash/file checks.
"""

import hashlib
import json
import tempfile
import unittest

from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from scripts.verify_backup_set import verify_set


class BackupSetTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="gs-backup-set-test-")
        self.addCleanup(temp.cleanup)
        self.directory = Path(temp.name) / "backup-set"
        self.directory.mkdir(mode=0o700)
        self.directory.chmod(0o700)

        self.files = self.directory / "files.tar.gz"
        self.volumes = self.directory / "volumes.tar.gz"
        self.manifest = self.directory / "backup-set.json"

        self.files.write_bytes(b"synthetic files archive")
        self.volumes.write_bytes(b"synthetic Caddy archive")
        self.files.chmod(0o600)
        self.volumes.chmod(0o600)

        def entry(path):
            raw = path.read_bytes()
            return {
                "name": path.name,
                "size": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }

        self.record = {
            "format": "garminsupla-backup-set/v1",
            "set_id": "a" * 32,
            "created_utc": "2026-11-15T09:00:00+00:00",
            "source_project": "gsfixture",
            "complete_system_backup": False,
            "offline_consistency_proven": False,
            "archives": {
                "files": entry(self.files),
                "caddy_volumes": entry(self.volumes),
            },
        }
        self.save(self.record)

        p1 = patch("scripts.verify_backup_set.verify_files", return_value=9)
        p2 = patch("scripts.verify_backup_set.verify_volumes", return_value=2)
        p1.start()
        p2.start()
        self.addCleanup(p1.stop)
        self.addCleanup(p2.stop)

    def save(self, data):
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        self.manifest.chmod(0o600)

    def rejects(self):
        with self.assertRaises((OSError, ValueError, RuntimeError)):
            verify_set(self.manifest)

    def test_valid_manifest(self):
        self.assertEqual(verify_set(self.manifest), (9, 2))

    def test_duplicate_json_field(self):
        source = self.manifest.read_text(encoding="utf-8")
        self.manifest.write_text(
            source.replace(
                '"format":',
                '"format": "garminsupla-backup-set/v1", "format":',
                1,
            ),
            encoding="utf-8",
        )
        self.rejects()

    def test_rejects_malformed_metadata(self):
        changes = (
            ("file traversal", lambda x: x["archives"]["files"].update(name="../x")),
            ("duplicate filenames", lambda x: x["archives"]["files"].update(name="volumes.tar.gz")),
            ("unproved completeness", lambda x: x.update(complete_system_backup=True)),
            ("unproved consistency", lambda x: x.update(offline_consistency_proven=True)),
            ("wrong size", lambda x: x["archives"]["files"].update(size=999)),
            ("wrong digest", lambda x: x["archives"]["files"].update(sha256="0" * 64)),
        )
        for label, change in changes:
            with self.subTest(label=label):
                candidate = deepcopy(self.record)
                change(candidate)
                self.save(candidate)
                self.rejects()

    def test_rejects_insecure_permissions(self):
        for target, mode in (
            (self.manifest, 0o644),
            (self.volumes, 0o644),
            (self.directory, 0o755),
        ):
            with self.subTest(path=target.name):
                previous = target.stat().st_mode & 0o777
                target.chmod(mode)
                try:
                    self.rejects()
                finally:
                    target.chmod(previous)

    def test_rejects_archive_symlink(self):
        moved = self.directory / "original.tar.gz"
        self.files.rename(moved)
        self.files.symlink_to(moved.name)
        try:
            self.rejects()
        finally:
            self.files.unlink()
            moved.rename(self.files)

    def test_rejects_archive_mutation(self):
        def mutate(_path):
            self.files.write_bytes(b"changed while verifying")
            return 9

        with patch("scripts.verify_backup_set.verify_files", side_effect=mutate):
            self.rejects()


if __name__ == "__main__":
    unittest.main()
