"""Isolated tests for the paired backup-set coordinator (no Docker or secrets)."""

import hashlib
import json
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.create_backup_set import create_backup_set


class CreateBackupSetTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="gs-set-create-test-")
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.root = self.base / "installation"
        self.certs = self.base / "certificates"
        self.parent = self.base / "sets"
        self.output = self.parent / "set-01"
        for d in (self.root, self.certs, self.parent):
            d.mkdir(mode=0o700)
            d.chmod(0o700)

        self.calls = []
        self.patches = (
            patch("scripts.create_backup_set._check_compose_project", side_effect=self._check_project),
            patch("scripts.create_backup_set.check_services_stopped", side_effect=self._check_offline),
            patch("scripts.create_backup_set.validate_volumes", side_effect=self._validate),
            patch("scripts.create_backup_set.create_backup", side_effect=self._files),
            patch("scripts.create_backup_set.create_caddy_volume_backup", side_effect=self._volumes),
            patch("scripts.create_backup_set.verify_set", side_effect=self._verify),
        )
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def _check_project(self, root, project):
        self.assertEqual((root, project), (self.root, "gstest"))
        self.calls.append("project-checked")

    def _check_offline(self, root):
        self.assertEqual(root, self.root)
        self.calls.append("offline")

    def _validate(self, project):
        self.assertEqual(project, "gstest")
        self.calls.append("volumes-checked")
        return ("gstest_garminsupla_caddy_data", "gstest_garminsupla_caddy_config")

    def _files(self, root, cert_dir, output):
        self.assertEqual((root, cert_dir), (self.root, self.certs))
        self.calls.append("files-created")
        output.write_bytes(b"fixture:files")
        output.chmod(0o600)

    def _volumes(self, project, image, root, cert_dir, output):
        self.assertEqual((project, image, root, cert_dir), ("gstest", "sha256:fixture", self.root, self.certs))
        self.calls.append("volumes-created")
        output.write_bytes(b"fixture:volumes")
        output.chmod(0o600)

    def _verify(self, path):
        self.assertEqual(path.name, ".backup-set.json.partial")
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(set(data), {"format", "set_id", "created_utc", "source_project", "complete_system_backup", "offline_consistency_proven", "archives"})
        self.assertEqual(data["format"], "garminsupla-backup-set/v1")
        self.assertEqual(len(data["set_id"]), 32)
        self.assertEqual(data["source_project"], "gstest")
        self.assertIs(data["complete_system_backup"], False)
        self.assertIs(data["offline_consistency_proven"], False)
        for kind, name in (("files", "files.tar.gz"), ("caddy_volumes", "volumes.tar.gz")):
            content = (self.output / name).read_bytes()
            self.assertEqual(data["archives"][kind], {
                "name": name,
                "size": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            })
        self.calls.append("verified")
        return (9, 2)

    def run_creator(self):
        return create_backup_set(self.root, self.certs, "gstest", "sha256:fixture", self.output)

    def test_valid_set_is_published_after_verification(self):
        self.assertEqual(self.run_creator(), (9, 2))
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o700)
        self.assertTrue((self.output / "backup-set.json").is_file())
        self.assertFalse((self.output / ".backup-set.json.partial").exists())
        self.assertEqual(self.calls.count("verified"), 1)
        self.assertLess(self.calls.index("files-created"), self.calls.index("volumes-created"))
        self.assertLess(self.calls.index("volumes-created"), self.calls.index("verified"))

    def test_existing_output_is_not_overwritten(self):
        self.output.mkdir(mode=0o700)
        marker = self.output / "keep"
        marker.write_text("preserve", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            self.run_creator()
        self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")
        self.assertEqual(self.calls, [])

    def test_nonprivate_parent_is_rejected(self):
        self.parent.chmod(0o755)
        with self.assertRaisesRegex(ValueError, "0700"):
            self.run_creator()
        self.assertFalse(self.output.exists())

    def test_source_directory_is_rejected_as_destination(self):
        self.output = self.root / "set-01"
        with self.assertRaisesRegex(ValueError, "outside installation"):
            self.run_creator()
        self.assertFalse(self.output.exists())

    def test_relative_source_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be absolute"):
            create_backup_set(
                Path("installation"), self.certs,
                "gstest", "sha256:fixture", self.output,
            )
        self.assertFalse(self.output.exists())

    def test_wrong_compose_project_is_rejected(self):
        with patch(
            "scripts.create_backup_set._check_compose_project",
            side_effect=ValueError("project mismatch"),
        ):
            with self.assertRaisesRegex(ValueError, "project mismatch"):
                self.run_creator()
        self.assertFalse(self.output.exists())

    def test_failed_preflight_creates_no_directory(self):
        with patch("scripts.create_backup_set.validate_volumes", side_effect=RuntimeError("offline failed")):
            with self.assertRaisesRegex(RuntimeError, "offline failed"):
                self.run_creator()
        self.assertFalse(self.output.exists())

    def test_failed_verification_never_publishes_manifest(self):
        with patch("scripts.create_backup_set.verify_set", side_effect=ValueError("invalid archive")):
            with self.assertRaisesRegex(ValueError, "invalid archive"):
                self.run_creator()
        self.assertTrue((self.output / "files.tar.gz").exists())
        self.assertTrue((self.output / "volumes.tar.gz").exists())
        self.assertFalse((self.output / "backup-set.json").exists())
        self.assertFalse((self.output / ".backup-set.json.partial").exists())

    def test_insecure_archive_is_rejected(self):
        def corrupt(_project, _image, _root, _cert_dir, output):
            output.write_bytes(b"bad")
            output.chmod(0o644)
        with patch("scripts.create_backup_set.create_caddy_volume_backup", side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, "private"):
                self.run_creator()
        self.assertFalse((self.output / "backup-set.json").exists())


if __name__ == "__main__":
    unittest.main()
