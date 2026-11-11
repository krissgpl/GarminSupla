import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

from scripts.check_caddy_volumes import VOLUMES
from scripts.restore_caddy_volumes import (
    TOKEN_LABEL,
    _create_volume,
    _owner,
    _run_writer,
    restore,
)


SOURCE = "gsarchive"
TARGET = "gsrestoreabc12345"
IMAGE = "sha256:" + "a" * 64


class RestoreCaddyVolumesTests(unittest.TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        self.directory = Path(temporary.name)
        self.archive = (
            self.directory / "synthetic.tar.gz"
        )

        self.names = tuple(
            f"{TARGET}_{short}"
            for short in VOLUMES
        )

        self.inner = self.make_inner(
            b"synthetic-volume-content"
        )

        self.make_archive()

        self.created = []
        self.removed = []
        self.written = {}

    @staticmethod
    def make_inner(content):
        buffer = io.BytesIO()

        with tarfile.open(
            fileobj=buffer,
            mode="w",
        ) as tar:

            folder = tarfile.TarInfo("nested/")
            folder.type = tarfile.DIRTYPE
            folder.mode = 0o700
            tar.addfile(folder)

            item = tarfile.TarInfo(
                "nested/state.txt"
            )

            item.size = len(content)
            item.mode = 0o600

            tar.addfile(
                item,
                io.BytesIO(content),
            )

        return buffer.getvalue()

    def make_archive(self, *, missing=False):
        records = []
        members = {}

        for short in VOLUMES:
            name = f"volumes/{short}.tar"

            records.append({
                "volume": f"{SOURCE}_{short}",
                "member": name,
                "size": len(self.inner),
                "sha256": hashlib.sha256(
                    self.inner
                ).hexdigest(),
            })

            if (
                not missing
                or short != VOLUMES[1]
            ):
                members[name] = self.inner

        members["manifest.json"] = json.dumps({
            "format": "garminsupla-caddy-volumes/v1",
            "complete_system_backup": False,
            "volumes": records,
        }).encode()

        with tarfile.open(
            self.archive,
            "w:gz",
        ) as tar:

            for name, data in members.items():
                item = tarfile.TarInfo(name)
                item.size = len(data)
                item.mode = 0o600

                tar.addfile(
                    item,
                    io.BytesIO(data),
                )

        self.archive.chmod(0o600)

    def run_mocked(
        self,
        *,
        writer_error=False,
        bad_read=False,
        create_error=None,
        cleanup_error=False,
    ):
        def create(name, short, project, token):
            self.assertEqual(project, TARGET)
            self.assertIn(short, VOLUMES)

            if create_error == "foreign":
                raise RuntimeError(
                    "synthetic create failure"
                )

            self.created.append(name)

            if create_error == "owned":
                raise RuntimeError(
                    "synthetic create failure"
                )

        def owner(name, token):
            return name in self.created

        def writer(name, image, source):
            self.assertEqual(image, IMAGE)

            if writer_error:
                raise RuntimeError(
                    "synthetic writer failure"
                )

            self.written[name] = (
                source.read_bytes()
            )

        def reader(name, image, destination):
            self.assertEqual(image, IMAGE)

            destination.write_bytes(
                self.make_inner(b"altered")
                if bad_read
                else self.written[name]
            )

        def docker(*args):
            self.assertEqual(
                args[:2],
                ("volume", "rm"),
            )

            self.removed.append(args[2])

            if cleanup_error:
                raise RuntimeError(
                    "synthetic remove failure"
                )

            return ""

        with (
            patch(
                "scripts.restore_caddy_volumes.validate_restore_target",
                return_value=self.names,
            ),
            patch(
                "scripts.restore_caddy_volumes.check_target",
                return_value=self.names,
            ),
            patch(
                "scripts.restore_caddy_volumes._create_volume",
                side_effect=create,
            ),
            patch(
                "scripts.restore_caddy_volumes._owner",
                side_effect=owner,
            ),
            patch(
                "scripts.restore_caddy_volumes._run_writer",
                side_effect=writer,
            ),
            patch(
                "scripts.restore_caddy_volumes.read_volume",
                side_effect=reader,
            ),
            patch(
                "scripts.restore_caddy_volumes._docker",
                side_effect=docker,
            ),
        ):
            return restore(
                self.archive,
                SOURCE,
                TARGET,
                IMAGE,
            )

    def test_synthetic_archive_passes_real_verifier(self):
        from scripts.verify_caddy_volume_backup import (
            verify_archive,
        )

        self.assertEqual(
            verify_archive(
                self.archive,
                SOURCE,
            ),
            2,
        )

    def test_success_restores_both_and_preserves_archive(self):
        before = hashlib.sha256(
            self.archive.read_bytes()
        ).hexdigest()

        self.assertEqual(
            self.run_mocked(),
            self.names,
        )

        self.assertEqual(
            self.created,
            list(self.names),
        )

        self.assertEqual(
            set(self.written),
            set(self.names),
        )

        self.assertEqual(self.removed, [])

        self.assertTrue(
            all(
                value == self.inner
                for value in self.written.values()
            )
        )

        self.assertEqual(
            hashlib.sha256(
                self.archive.read_bytes()
            ).hexdigest(),
            before,
        )

        self.assertEqual(
            sorted(
                path.name
                for path in self.directory.iterdir()
            ),
            [self.archive.name],
        )

    def test_rejects_unpinned_image(self):
        for image in (
            "python:3.13",
            "sha256:123",
            "-bad",
            "",
        ):
            with self.subTest(image=image):
                with self.assertRaisesRegex(
                    ValueError,
                    "pinned sha256",
                ):
                    restore(
                        self.archive,
                        SOURCE,
                        TARGET,
                        image,
                    )

    def test_symlink_source_is_rejected(self):
        link = (
            self.directory / "alias.tar.gz"
        )

        link.symlink_to(self.archive)

        with self.assertRaises(OSError):
            restore(
                link,
                SOURCE,
                TARGET,
                IMAGE,
            )

    def test_failed_archive_check_creates_no_volumes(self):
        with (
            patch(
                "scripts.restore_caddy_volumes.validate_restore_target",
                side_effect=ValueError(
                    "synthetic invalid archive"
                ),
            ),
            patch(
                "scripts.restore_caddy_volumes._create_volume"
            ) as create,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "invalid archive",
            ):
                restore(
                    self.archive,
                    SOURCE,
                    TARGET,
                    IMAGE,
                )

            create.assert_not_called()

    def test_missing_inner_tar_creates_no_volumes(self):
        self.make_archive(missing=True)

        with (
            patch(
                "scripts.restore_caddy_volumes.validate_restore_target",
                return_value=self.names,
            ),
            patch(
                "scripts.restore_caddy_volumes._create_volume"
            ) as create,
        ):
            with self.assertRaises(KeyError):
                restore(
                    self.archive,
                    SOURCE,
                    TARGET,
                    IMAGE,
                )

            create.assert_not_called()

    def test_writer_failure_cleans_owned_volumes(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "writer failure",
        ):
            self.run_mocked(
                writer_error=True
            )

        self.assertEqual(
            self.removed,
            list(reversed(self.names)),
        )

    def test_mismatched_restored_data_cleans_owned_volumes(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "differs from backup",
        ):
            self.run_mocked(
                bad_read=True
            )

        self.assertEqual(
            self.removed,
            list(reversed(self.names)),
        )

    def test_failed_creation_cleans_only_owned_volume(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "create failure",
        ):
            self.run_mocked(
                create_error="owned"
            )

        self.assertEqual(
            self.removed,
            [self.names[0]],
        )

    def test_foreign_volume_never_removed(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "create failure",
        ):
            self.run_mocked(
                create_error="foreign"
            )

        self.assertEqual(
            self.removed,
            [],
        )

    def test_cleanup_failure_is_reported(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "cleanup incomplete",
        ):
            self.run_mocked(
                writer_error=True,
                cleanup_error=True,
            )

        self.assertEqual(
            self.removed,
            list(reversed(self.names)),
        )

    def test_owner_checks_unique_token(self):
        name = self.names[0]

        metadata = [{
            "Name": name,
            "Driver": "local",
            "Scope": "local",
            "Options": None,
            "Labels": {
                TOKEN_LABEL: "my-token",
            },
        }]

        with patch(
            "scripts.restore_caddy_volumes._docker",
            return_value=json.dumps(metadata),
        ):
            self.assertTrue(
                _owner(name, "my-token")
            )

            self.assertFalse(
                _owner(name, "another-token")
            )

        metadata[0]["Driver"] = "other"

        with patch(
            "scripts.restore_caddy_volumes._docker",
            return_value=json.dumps(metadata),
        ):
            self.assertFalse(
                _owner(name, "my-token")
            )

    def test_create_volume_validates_identity(self):
        with (
            patch(
                "scripts.restore_caddy_volumes._docker",
                return_value=self.names[0],
            ) as docker,
            patch(
                "scripts.restore_caddy_volumes._owner",
                return_value=True,
            ),
        ):
            _create_volume(
                self.names[0],
                VOLUMES[0],
                TARGET,
                "token",
            )

            self.assertIn(
                f"{TOKEN_LABEL}=token",
                docker.call_args.args,
            )

            self.assertIn(
                f"com.docker.compose.project={TARGET}",
                docker.call_args.args,
            )

        with (
            patch(
                "scripts.restore_caddy_volumes._docker",
                return_value=self.names[0],
            ),
            patch(
                "scripts.restore_caddy_volumes._owner",
                return_value=False,
            ),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "identity mismatch",
            ):
                _create_volume(
                    self.names[0],
                    VOLUMES[0],
                    TARGET,
                    "token",
                )

    def test_writer_docker_run_is_restricted(self):
        source = (
            self.directory / "inner.tar"
        )

        source.write_bytes(self.inner)

        with patch(
            "scripts.restore_caddy_volumes.subprocess.run"
        ) as run:
            run.return_value.returncode = 0

            _run_writer(
                self.names[0],
                IMAGE,
                source,
            )

            command = run.call_args.args[0]

            self.assertEqual(
                command[:2],
                ["docker", "run"],
            )

            self.assertIn(
                "none",
                command,
            )

            self.assertIn(
                "--read-only",
                command,
            )

            self.assertIn(
                "--cap-drop",
                command,
            )

            self.assertIn(
                "--cap-add",
                command,
            )

            self.assertIn(
                "CHOWN",
                command,
            )

            self.assertIn(
                "no-new-privileges:true",
                command,
            )

            self.assertIn(
                (
                    f"type=volume,source={self.names[0]},"
                    "target=/restore,volume-nocopy"
                ),
                command,
            )

    def test_cli_requires_explicit_confirmation(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "scripts.restore_caddy_volumes",
                "--archive",
                str(self.archive),
                "--source-project",
                SOURCE,
                "--target-project",
                TARGET,
                "--image",
                IMAGE,
            ],
            cwd=Path(__file__).resolve().parent.parent,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(
            result.returncode,
            0,
        )

        self.assertIn(
            "--confirm-isolated",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
