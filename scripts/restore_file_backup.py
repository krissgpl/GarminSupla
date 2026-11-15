"""Restore a verified GarminSupla file archive into a new isolated directory.

Never overwrites existing files or restores into an existing target.
Does not contact Docker or change the running installation.
"""

import argparse
import hashlib
import json
import os
import shutil
import stat
import sys
import tarfile
import tempfile
from pathlib import Path

from scripts.check_file_restore_target import (
    check_target,
    validate_restore_target,
)
from scripts.verify_file_backup import allowed_name


CHUNK = 1024 * 1024
DIR_FLAGS = (
    os.O_RDONLY
    | os.O_DIRECTORY
    | os.O_NOFOLLOW
)
FILE_FLAGS = (
    os.O_WRONLY
    | os.O_CREAT
    | os.O_EXCL
    | os.O_NOFOLLOW
)


def _private_copy(
    source: Path,
    destination: Path,
) -> None:
    """Copy only a regular, owner-only archive, without links."""

    before = source.lstat()

    if (
        not stat.S_ISREG(before.st_mode)
        or stat.S_IMODE(before.st_mode) & 0o077
    ):
        raise ValueError(
            "Backup must be a regular owner-only file"
        )

    fd = os.open(
        source,
        os.O_RDONLY | os.O_NOFOLLOW,
    )

    with os.fdopen(fd, "rb") as input_file:
        current = os.fstat(input_file.fileno())

        if (
            not stat.S_ISREG(current.st_mode)
            or stat.S_IMODE(current.st_mode) & 0o077
            or (
                before.st_dev,
                before.st_ino,
            ) != (
                current.st_dev,
                current.st_ino,
            )
        ):
            raise ValueError(
                "Backup source changed or is not owner-only"
            )

        output_fd = os.open(
            destination,
            FILE_FLAGS,
            0o600,
        )

        with os.fdopen(output_fd, "wb") as output:
            shutil.copyfileobj(
                input_file,
                output,
                CHUNK,
            )

            output.flush()
            os.fsync(output.fileno())


def _walk(
    root_fd: int,
    parts: tuple[str, ...],
    directories=None,
) -> int:
    """Open subdirectories without following symlinks."""

    fd = os.dup(root_fd)
    prefix = ()

    try:
        for part in parts:
            prefix += (part,)

            if (
                directories is not None
                and prefix not in directories
            ):
                os.mkdir(
                    part,
                    mode=0o700,
                    dir_fd=fd,
                )

                directories.append(prefix)

            child = os.open(
                part,
                DIR_FLAGS,
                dir_fd=fd,
            )

            os.close(fd)
            fd = child

        return fd

    except BaseException:
        os.close(fd)
        raise


def _extract(
    archive_path: Path,
    root_fd: int,
    files: list,
    dirs: list,
) -> int:
    """Write files exclusively and verify their contents."""

    with tarfile.open(
        archive_path,
        mode="r:gz",
    ) as archive:

        manifest_source = archive.extractfile(
            "manifest.json"
        )

        if manifest_source is None:
            raise ValueError(
                "Missing verified backup manifest"
            )

        manifest = json.load(manifest_source)

        expected = {
            item["path"]: item
            for item in manifest["files"]
        }

        written = set()

        for member in archive:
            if member.name == "manifest.json":
                continue

            name = member.name

            if (
                not allowed_name(name)
                or name in written
                or name not in expected
                or not member.isfile()
                or member.mode != 0o600
            ):
                raise ValueError(
                    "Unsafe restore archive entry"
                )

            parts = tuple(name.split("/"))

            parent_fd = _walk(
                root_fd,
                parts[:-1],
                dirs,
            )

            try:
                source = archive.extractfile(
                    member
                )

                if source is None:
                    raise ValueError(
                        "Unreadable restore archive entry"
                    )

                output_fd = os.open(
                    parts[-1],
                    FILE_FLAGS,
                    0o600,
                    dir_fd=parent_fd,
                )

                files.append(parts)

                with os.fdopen(
                    output_fd,
                    "wb",
                ) as target:

                    digest = hashlib.sha256()
                    size = 0

                    while True:
                        chunk = source.read(CHUNK)

                        if not chunk:
                            break

                        target.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)

                    os.fchmod(
                        target.fileno(),
                        0o600,
                    )

                    target.flush()
                    os.fsync(target.fileno())

                if (
                    size != expected[name]["size"]
                    or digest.hexdigest()
                    != expected[name]["sha256"]
                ):
                    raise ValueError(
                        "Restore archive content mismatch"
                    )

                written.add(name)

            finally:
                os.close(parent_fd)

        if written != set(expected):
            raise ValueError(
                "Incomplete restore archive contents"
            )

    # Independently read back files from the destination.
    for name, record in expected.items():
        parts = tuple(name.split("/"))

        parent_fd = _walk(
            root_fd,
            parts[:-1],
        )

        try:
            fd = os.open(
                parts[-1],
                os.O_RDONLY | os.O_NOFOLLOW,
                dir_fd=parent_fd,
            )

            with os.fdopen(fd, "rb") as restored:
                info = os.fstat(
                    restored.fileno()
                )

                if (
                    not stat.S_ISREG(info.st_mode)
                    or stat.S_IMODE(info.st_mode) != 0o600
                    or info.st_uid != os.geteuid()
                ):
                    raise RuntimeError(
                        "Restored file metadata mismatch"
                    )

                digest = hashlib.sha256()
                size = 0

                while True:
                    chunk = restored.read(CHUNK)

                    if not chunk:
                        break

                    digest.update(chunk)
                    size += len(chunk)

                if (
                    size != record["size"]
                    or digest.hexdigest()
                    != record["sha256"]
                ):
                    raise RuntimeError(
                        "Restored file verification failed"
                    )

        finally:
            os.close(parent_fd)

    return len(written)


def _cleanup(
    root_fd: int,
    parent_fd: int,
    name: str,
    identity: tuple,
    files: list,
    dirs: list,
) -> None:
    """Remove tracked entries only if target identity is unchanged."""

    current = os.stat(
        name,
        dir_fd=parent_fd,
        follow_symlinks=False,
    )

    if (
        not stat.S_ISDIR(current.st_mode)
        or (
            current.st_dev,
            current.st_ino,
        ) != identity
    ):
        raise RuntimeError(
            "Restore target identity changed; "
            "manual cleanup required"
        )

    for parts in reversed(files):
        fd = _walk(
            root_fd,
            parts[:-1],
        )

        try:
            os.unlink(
                parts[-1],
                dir_fd=fd,
            )
        finally:
            os.close(fd)

    for parts in reversed(dirs):
        fd = _walk(
            root_fd,
            parts[:-1],
        )

        try:
            os.rmdir(
                parts[-1],
                dir_fd=fd,
            )
        finally:
            os.close(fd)

    os.rmdir(
        name,
        dir_fd=parent_fd,
    )

    os.fsync(parent_fd)


def restore_file_backup(
    archive: Path,
    target: Path,
) -> int:
    """Restore only into a new isolated gsrestore directory."""

    archive = Path(archive)
    target = Path(target)

    # Stage a private snapshot outside the restore destination.
    with tempfile.TemporaryDirectory(
        prefix="gs-file-restore-"
    ) as temp:

        snapshot = (
            Path(temp) / "backup.tar.gz"
        )

        _private_copy(
            archive,
            snapshot,
        )

        # Full archive verification before creating target.
        destination, count = validate_restore_target(
            snapshot,
            target,
        )

        if check_target(destination) != destination:
            raise RuntimeError(
                "Restore destination changed"
            )

        parent = destination.parent
        before = parent.lstat()

        parent_fd = os.open(
            parent,
            DIR_FLAGS,
        )

        target_fd = None
        created = False
        files = []
        dirs = []
        identity = None

        try:
            actual = os.fstat(parent_fd)

            if (
                (
                    actual.st_dev,
                    actual.st_ino,
                ) != (
                    before.st_dev,
                    before.st_ino,
                )
                or actual.st_uid != os.geteuid()
                or stat.S_IMODE(actual.st_mode)
                != 0o700
            ):
                raise RuntimeError(
                    "Restore parent identity changed"
                )

            # mkdir is exclusive: existing target is never reused.
            os.mkdir(
                destination.name,
                mode=0o700,
                dir_fd=parent_fd,
            )

            created = True

            target_fd = os.open(
                destination.name,
                DIR_FLAGS,
                dir_fd=parent_fd,
            )

            info = os.fstat(target_fd)

            identity = (
                info.st_dev,
                info.st_ino,
            )

            os.fchmod(
                target_fd,
                0o700,
            )

            restored = _extract(
                snapshot,
                target_fd,
                files,
                dirs,
            )

            if restored != count:
                raise RuntimeError(
                    "Restore file count mismatch"
                )

            os.fsync(target_fd)
            os.fsync(parent_fd)

            return restored

        except BaseException as exc:
            if created:
                if (
                    target_fd is None
                    or identity is None
                ):
                    raise RuntimeError(
                        "Restore failed; target cleanup "
                        "requires manual inspection"
                    ) from exc

                try:
                    _cleanup(
                        target_fd,
                        parent_fd,
                        destination.name,
                        identity,
                        files,
                        dirs,
                    )

                except BaseException as cleanup_exc:
                    raise RuntimeError(
                        "Restore failed; cleanup incomplete for "
                        + str(destination)
                    ) from cleanup_exc

            raise

        finally:
            if target_fd is not None:
                os.close(target_fd)

            os.close(parent_fd)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
    )

    parser.add_argument(
        "--archive",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--target",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--confirm-isolated",
        action="store_true",
    )

    args = parser.parse_args()

    if not args.confirm_isolated:
        print(
            "ERROR: --confirm-isolated is required",
            file=sys.stderr,
        )
        return 1

    try:
        count = restore_file_backup(
            args.archive,
            args.target,
        )

    except (
        OSError,
        ValueError,
        RuntimeError,
        tarfile.TarError,
    ) as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: restored and verified {count} "
        "isolated GarminSupla files"
    )

    print(
        "INFO: Caddy Docker volumes not restored; "
        "not a complete recovery"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
