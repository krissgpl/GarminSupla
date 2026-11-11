import hashlib
import io
import json
import tarfile
import tempfile
import unittest

from pathlib import Path

from scripts.verify_caddy_volume_backup import (
    verify_archive,
)


class VerifyCaddyVolumeBackupTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.path = (
            Path(self.temp.name) / "caddy.tar.gz"
        )
        self.project = "gstest"

    def make_inner(self, *, dangerous=None):
        buffer = io.BytesIO()

        with tarfile.open(
            fileobj=buffer,
            mode="w",
        ) as archive:

            if dangerous == "link":
                info = tarfile.TarInfo("link")
                info.type = tarfile.SYMTYPE
                info.linkname = "/etc/passwd"
                archive.addfile(info)

            else:
                name = (
                    "../escape"
                    if dangerous == "traversal"
                    else "nested/value.txt"
                )

                for _ in range(
                    2 if dangerous == "duplicate" else 1
                ):
                    content = b"synthetic Caddy data"

                    info = tarfile.TarInfo(name)
                    info.size = len(content)
                    info.mode = 0o600

                    archive.addfile(
                        info,
                        io.BytesIO(content),
                    )

        return buffer.getvalue()

    def make_backup(
        self,
        *,
        dangerous=None,
        wrong_hash=False,
        missing=False,
        wrong_project=False,
        wrong_format=False,
        extra=False,
    ):
        records = []
        contents = {}

        for name in (
            "garminsupla_caddy_data",
            "garminsupla_caddy_config",
        ):
            payload = self.make_inner(
                dangerous=dangerous
            )

            member = f"volumes/{name}.tar"
            contents[member] = payload

            records.append({
                "volume": (
                    f"{'other' if wrong_project else self.project}"
                    f"_{name}"
                ),
                "member": member,
                "size": len(payload),
                "sha256": (
                    "0" * 64
                    if wrong_hash
                    else hashlib.sha256(
                        payload
                    ).hexdigest()
                ),
            })

        manifest = {
            "format": (
                "wrong"
                if wrong_format
                else "garminsupla-caddy-volumes/v1"
            ),
            "complete_system_backup": False,
            "volumes": records,
        }

        contents["manifest.json"] = json.dumps(
            manifest
        ).encode()

        if missing:
            contents.pop(
                "volumes/garminsupla_caddy_data.tar"
            )

        if extra:
            contents["other"] = b"extra"

        with tarfile.open(
            self.path,
            "w:gz",
        ) as outer:

            for name, content in contents.items():
                info = tarfile.TarInfo(name)
                info.size = len(content)
                info.mode = 0o600

                outer.addfile(
                    info,
                    io.BytesIO(content),
                )

        self.path.chmod(0o600)

    def test_valid(self):
        self.make_backup()

        self.assertEqual(
            verify_archive(
                self.path,
                self.project,
            ),
            2,
        )

    def test_wrong_hash(self):
        self.make_backup(wrong_hash=True)

        with self.assertRaisesRegex(
            ValueError,
            "SHA-256",
        ):
            verify_archive(
                self.path,
                self.project,
            )

    def test_missing(self):
        self.make_backup(missing=True)

        with self.assertRaisesRegex(
            ValueError,
            "Unexpected outer",
        ):
            verify_archive(
                self.path,
                self.project,
            )

    def test_extra(self):
        self.make_backup(extra=True)

        with self.assertRaisesRegex(
            ValueError,
            "Unexpected outer",
        ):
            verify_archive(
                self.path,
                self.project,
            )

    def test_wrong_project(self):
        self.make_backup(
            wrong_project=True
        )

        with self.assertRaisesRegex(
            ValueError,
            "manifest record",
        ):
            verify_archive(
                self.path,
                self.project,
            )

    def test_wrong_format(self):
        self.make_backup(
            wrong_format=True
        )

        with self.assertRaisesRegex(
            ValueError,
            "manifest",
        ):
            verify_archive(
                self.path,
                self.project,
            )

    def test_traversal(self):
        self.make_backup(
            dangerous="traversal"
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsafe",
        ):
            verify_archive(
                self.path,
                self.project,
            )

    def test_link(self):
        self.make_backup(
            dangerous="link"
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsafe",
        ):
            verify_archive(
                self.path,
                self.project,
            )

    def test_duplicate(self):
        self.make_backup(
            dangerous="duplicate"
        )

        with self.assertRaisesRegex(
            ValueError,
            "Unsafe",
        ):
            verify_archive(
                self.path,
                self.project,
            )

    def test_weak_permissions(self):
        self.make_backup()
        self.path.chmod(0o644)

        with self.assertRaisesRegex(
            ValueError,
            "owner-only",
        ):
            verify_archive(
                self.path,
                self.project,
            )

    def test_corrupt_gzip(self):
        self.path.write_bytes(
            b"not gzip"
        )
        self.path.chmod(0o600)

        with self.assertRaisesRegex(
            ValueError,
            "Invalid",
        ):
            verify_archive(
                self.path,
                self.project,
            )

    def test_invalid_project(self):
        self.make_backup()

        with self.assertRaisesRegex(
            ValueError,
            "Invalid Docker Compose",
        ):
            verify_archive(
                self.path,
                "../other",
            )

    def test_no_files_written(self):
        self.make_backup()

        before = sorted(
            path.name
            for path in self.path.parent.iterdir()
        )

        verify_archive(
            self.path,
            self.project,
        )

        after = sorted(
            path.name
            for path in self.path.parent.iterdir()
        )

        self.assertEqual(
            before,
            after,
        )


if __name__ == "__main__":
    unittest.main()
