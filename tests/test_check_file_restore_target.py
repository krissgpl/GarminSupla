import os
import subprocess
import sys
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from scripts.check_file_restore_target import (
    check_target,
    validate_restore_target,
)


ROOT = Path(__file__).resolve().parent.parent


class FileRestoreTargetTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        self.base = Path(temporary.name)
        self.parent = self.base / "private"
        self.parent.mkdir(mode=0o700)
        self.parent.chmod(0o700)

        self.target = (
            self.parent / "gsrestoreabc12345"
        )

        self.archive = (
            self.base / "synthetic.tar.gz"
        )

    def test_unused_target_accepted(self):
        result = check_target(self.target)

        self.assertEqual(
            result,
            self.target,
        )

        self.assertFalse(
            self.target.exists()
        )

    def test_relative_target_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "absolute",
        ):
            check_target(
                Path("gsrestoreabc12345")
            )

    def test_unrelated_target_name_rejected(self):
        for name in (
            "garminsupla",
            "production",
            "gsrestoreabc",
            "gsrestoreABC12345",
        ):
            with self.subTest(name=name):
                with self.assertRaisesRegex(
                    ValueError,
                    "gsrestore",
                ):
                    check_target(
                        self.parent / name
                    )

    def test_existing_directory_rejected(self):
        self.target.mkdir()

        with self.assertRaisesRegex(
            FileExistsError,
            "already exists",
        ):
            check_target(self.target)

    def test_existing_file_rejected(self):
        self.target.write_bytes(
            b"preserve-existing"
        )

        with self.assertRaises(
            FileExistsError
        ):
            check_target(self.target)

        self.assertEqual(
            self.target.read_bytes(),
            b"preserve-existing",
        )

    def test_dangling_symlink_rejected(self):
        self.target.symlink_to(
            self.base / "missing"
        )

        with self.assertRaises(
            FileExistsError
        ):
            check_target(self.target)

        self.assertTrue(
            self.target.is_symlink()
        )

    def test_weak_parent_permissions_rejected(self):
        self.parent.chmod(0o755)

        with self.assertRaisesRegex(
            ValueError,
            "0700",
        ):
            check_target(self.target)

    def test_unwritable_parent_rejected(self):
        self.parent.chmod(0o500)

        with self.assertRaisesRegex(
            ValueError,
            "0700",
        ):
            check_target(self.target)

    def test_parent_is_file_rejected(self):
        parent = self.base / "not-a-directory"
        parent.write_bytes(b"fixture")

        with self.assertRaisesRegex(
            ValueError,
            "real directory",
        ):
            check_target(
                parent / self.target.name
            )

    def test_parent_symlink_rejected(self):
        alias = self.base / "alias"
        alias.symlink_to(
            self.parent,
            target_is_directory=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            "without symlinks",
        ):
            check_target(
                alias / self.target.name
            )

    def test_symlink_ancestor_rejected(self):
        original = self.base / "original"
        original.mkdir(mode=0o700)
        original.chmod(0o700)

        nested = original / "nested"
        nested.mkdir(mode=0o700)
        nested.chmod(0o700)

        alias = self.base / "linked"
        alias.symlink_to(
            original,
            target_is_directory=True,
        )

        with self.assertRaisesRegex(
            ValueError,
            "without symlinks",
        ):
            check_target(
                alias / "nested" / self.target.name
            )

    def test_missing_parent_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "unavailable",
        ):
            check_target(
                self.base / "missing" / self.target.name
            )

    def test_wrong_owner_rejected(self):
        owner = self.parent.stat().st_uid

        with patch(
            "scripts.check_file_restore_target.os.geteuid",
            return_value=owner + 1,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "owned by current user",
            ):
                check_target(self.target)

    def test_dotdot_parent_rejected(self):
        target = (
            self.parent
            / ".."
            / self.target.name
        )

        with self.assertRaisesRegex(
            ValueError,
            "path traversal",
        ):
            check_target(target)

    def test_verification_precedes_target_check(self):
        with (
            patch(
                "scripts.check_file_restore_target.verify_archive",
                side_effect=ValueError(
                    "synthetic invalid archive"
                ),
            ),
            patch(
                "scripts.check_file_restore_target.check_target",
                side_effect=AssertionError(
                    "Target must not be inspected"
                ),
            ) as target_check,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "invalid archive",
            ):
                validate_restore_target(
                    self.archive,
                    self.target,
                )

            target_check.assert_not_called()

    def test_verified_archive_allows_target_check(self):
        with patch(
            "scripts.check_file_restore_target.verify_archive",
            return_value=9,
        ) as verifier:
            target, count = validate_restore_target(
                self.archive,
                self.target,
            )

        self.assertEqual(
            target,
            self.target,
        )

        self.assertEqual(
            count,
            9,
        )

        verifier.assert_called_once_with(
            self.archive
        )

        self.assertFalse(
            self.target.exists()
        )

    def test_cli_missing_archive_creates_nothing(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "scripts.check_file_restore_target",
                "--archive",
                str(self.archive),
                "--target",
                str(self.target),
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

        self.assertFalse(
            self.target.exists()
        )

    def test_cli_requires_arguments(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "scripts.check_file_restore_target",
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

        self.assertFalse(
            self.target.exists()
        )


if __name__ == "__main__":
    unittest.main()
