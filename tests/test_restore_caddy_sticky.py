"""Regression tests for sticky directory modes in Caddy restore."""

import io
import os
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest

from pathlib import Path

from scripts.restore_caddy_volumes import RESTORE_READER


class RestoreCaddyStickyTests(unittest.TestCase):

    def run_reader(self, directory_mode, file_mode=0o600):
        with tempfile.TemporaryDirectory(
            prefix="gssticky-"
        ) as temporary:

            destination = Path(temporary) / "volume"
            destination.mkdir(mode=0o700)

            content = b"synthetic-caddy-data"
            buffer = io.BytesIO()

            with tarfile.open(
                fileobj=buffer,
                mode="w",
            ) as archive:

                folder = tarfile.TarInfo("nested/")
                folder.type = tarfile.DIRTYPE
                folder.mode = directory_mode
                folder.uid = os.geteuid()
                folder.gid = os.getegid()
                archive.addfile(folder)

                item = tarfile.TarInfo("nested/state.txt")
                item.size = len(content)
                item.mode = file_mode
                item.uid = os.geteuid()
                item.gid = os.getegid()

                archive.addfile(
                    item,
                    io.BytesIO(content),
                )

            marker = 'ROOT = "/restore"'

            self.assertEqual(
                RESTORE_READER.count(marker),
                1,
            )

            reader = RESTORE_READER.replace(
                marker,
                "ROOT = " + repr(str(destination)),
                1,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-S",
                    "-c",
                    reader,
                ],
                input=buffer.getvalue(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
                check=False,
            )

            restored_mode = None
            restored_content = None

            if result.returncode == 0:
                folder = destination / "nested"
                restored_mode = stat.S_IMODE(
                    folder.stat().st_mode
                )
                restored_content = (
                    folder / "state.txt"
                ).read_bytes()

            return result, restored_mode, restored_content

    def test_accepts_sticky_directory(self):
        result, mode, content = self.run_reader(0o1777)

        self.assertEqual(
            result.returncode,
            0,
            result.stderr.decode(errors="replace"),
        )
        self.assertEqual(mode, 0o1777)
        self.assertEqual(content, b"synthetic-caddy-data")

    def test_rejects_setgid_directory(self):
        result, _, _ = self.run_reader(0o2777)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            b"Unsafe volume TAR entry",
            result.stderr,
        )

    def test_rejects_setuid_directory(self):
        result, _, _ = self.run_reader(0o4777)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            b"Unsafe volume TAR entry",
            result.stderr,
        )

    def test_rejects_sticky_regular_file(self):
        result, _, _ = self.run_reader(
            0o700,
            file_mode=0o1600,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            b"Unsafe volume TAR entry",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
