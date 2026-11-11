"""Restore verified Caddy TAR files only to new isolated Docker volumes.

Never use this tool against existing/production volumes.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import uuid
from pathlib import Path

from scripts.check_caddy_volumes import VOLUMES, _docker
from scripts.check_caddy_restore_target import (
    check_target,
    validate_restore_target,
)
from scripts.create_caddy_volume_backup import (
    read_volume,
    check_inner_tar,
    file_digest,
)


# Executed in a restricted helper container.
# Only the new target volume is mounted writable.
RESTORE_READER = r'''
import os
import sys
import tarfile

ROOT = "/restore"
DIR_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def parent_fd(parts):
    fd = os.open(ROOT, DIR_FLAGS)

    try:
        for part in parts:
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


with os.scandir(ROOT) as entries:
    if next(entries, None) is not None:
        raise RuntimeError(
            "Destination volume is not empty"
        )


seen = set()
directories = []

with tarfile.open(
    fileobj=sys.stdin.buffer,
    mode="r|",
) as archive:

    for member in archive:
        name = member.name.rstrip("/")
        parts = name.split("/")

        if (
            not name
            or name.startswith("/")
            or "\\" in name
            or any(
                x in ("", ".", "..")
                for x in parts
            )
            or name in seen
            or not (
                member.isdir()
                or member.isfile()
            )
            or member.mode & ~0o777
            or member.size < 0
            or member.uid < 0
            or member.gid < 0
        ):
            raise RuntimeError(
                "Unsafe volume TAR entry"
            )

        seen.add(name)
        parent = parent_fd(parts[:-1])

        try:
            leaf = parts[-1]

            if member.isdir():
                os.mkdir(
                    leaf,
                    0o700,
                    dir_fd=parent,
                )

                directories.append((
                    parts,
                    member.uid,
                    member.gid,
                    member.mode,
                ))

            else:
                source = archive.extractfile(
                    member
                )

                if source is None:
                    raise RuntimeError(
                        "Volume member unreadable"
                    )

                fd = os.open(
                    leaf,
                    os.O_WRONLY
                    | os.O_CREAT
                    | os.O_EXCL
                    | os.O_NOFOLLOW,
                    0o600,
                    dir_fd=parent,
                )

                with os.fdopen(fd, "wb") as target:
                    remaining = member.size

                    while remaining:
                        chunk = source.read(
                            min(
                                1024 * 1024,
                                remaining,
                            )
                        )

                        if not chunk:
                            raise RuntimeError(
                                "Truncated volume member"
                            )

                        target.write(chunk)
                        remaining -= len(chunk)

                    os.fchown(
                        target.fileno(),
                        member.uid,
                        member.gid,
                    )

                    os.fchmod(
                        target.fileno(),
                        member.mode,
                    )

                    target.flush()
                    os.fsync(
                        target.fileno()
                    )

        finally:
            os.close(parent)


# Apply final directory permissions after writing files.
for parts, uid, gid, mode in reversed(
    directories
):
    fd = parent_fd(parts)

    try:
        os.fchown(fd, uid, gid)
        os.fchmod(fd, mode)
        os.fsync(fd)

    finally:
        os.close(fd)
'''


TOKEN_LABEL = "org.garminsupla.restore-token"


def _owner(name: str, token: str) -> bool:
    """Verify ownership by this restore operation."""

    try:
        details = json.loads(
            _docker(
                "volume",
                "inspect",
                name,
            )
        )
    except (
        json.JSONDecodeError,
        RuntimeError,
    ):
        return False

    if (
        not isinstance(details, list)
        or len(details) != 1
        or not isinstance(details[0], dict)
    ):
        return False

    info = details[0]
    labels = info.get("Labels") or {}

    return (
        info.get("Name") == name
        and info.get("Driver") == "local"
        and info.get("Scope") == "local"
        and info.get("Options") in (None, {})
        and isinstance(labels, dict)
        and labels.get(TOKEN_LABEL) == token
    )


def _create_volume(
    name: str,
    short: str,
    project: str,
    token: str,
) -> None:
    output = _docker(
        "volume",
        "create",
        "--driver",
        "local",
        "--label",
        f"com.docker.compose.project={project}",
        "--label",
        f"com.docker.compose.volume={short}",
        "--label",
        f"{TOKEN_LABEL}={token}",
        name,
    )

    if (
        output != name
        or not _owner(name, token)
    ):
        raise RuntimeError(
            "Created volume identity mismatch"
        )


def _run_writer(
    volume: str,
    image: str,
    source: Path,
) -> None:
    name = (
        f"gs-restore-helper-{uuid.uuid4().hex}"
    )

    command = [
        "docker",
        "run",
        "--rm",
        "-i",
        "--name",
        name,
        "--pull",
        "never",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--cap-add",
        "CHOWN",
        "--security-opt",
        "no-new-privileges:true",
        "--pids-limit",
        "128",
        "--memory",
        "256m",
        "--cpus",
        "1",
        "--user",
        "0:0",
        "--mount",
        (
            f"type=volume,source={volume},"
            "target=/restore,volume-nocopy"
        ),
        "--entrypoint",
        "python",
        image,
        "-B",
        "-S",
        "-c",
        RESTORE_READER,
    ]

    try:
        with source.open("rb") as stream:
            result = subprocess.run(
                command,
                stdin=stream,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=300,
                check=False,
            )

    except (
        OSError,
        subprocess.TimeoutExpired,
    ) as exc:
        try:
            subprocess.run(
                [
                    "docker",
                    "rm",
                    "-f",
                    name,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15,
                check=False,
            )

        except (
            OSError,
            subprocess.TimeoutExpired,
        ):
            pass

        raise RuntimeError(
            "Restore helper unavailable or timed out"
        ) from exc

    if result.returncode:
        raise RuntimeError(
            "Restore helper failed"
        )


def _staged_members(
    archive: Path,
    directory: Path,
) -> dict:
    """Stage verified volume TARs privately."""

    result = {}

    with tarfile.open(
        archive,
        "r:gz",
    ) as outer:

        for short in VOLUMES:
            member = outer.getmember(
                f"volumes/{short}.tar"
            )

            destination = (
                directory / (short + ".tar")
            )

            source = outer.extractfile(
                member
            )

            if source is None:
                raise ValueError(
                    "Missing verified volume TAR"
                )

            fd = os.open(
                destination,
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL,
                0o600,
            )

            with os.fdopen(fd, "wb") as target:
                shutil.copyfileobj(
                    source,
                    target,
                    1024 * 1024,
                )

                target.flush()
                os.fsync(
                    target.fileno()
                )

            if (
                destination.stat().st_size
                != member.size
            ):
                raise ValueError(
                    "Staged volume TAR size mismatch"
                )

            result[short] = destination

    return result


def restore(
    archive: Path,
    source_project: str,
    target_project: str,
    image: str,
) -> tuple[str, ...]:
    """Restore only to newly owned isolated volumes."""

    if (
        not image.startswith("sha256:")
        or len(image) != 71
        or any(
            char not in "0123456789abcdef"
            for char in image[7:]
        )
    ):
        raise ValueError(
            "Image must be a pinned sha256 Docker image ID"
        )

    # Verify a private copy, not a mutable original path.
    with tempfile.TemporaryDirectory(
        prefix="gs-caddy-restore-"
    ) as temp:

        stage = Path(temp)
        staged_archive = (
            stage / "backup.tar.gz"
        )

        flags = (
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
        )

        fd = os.open(
            archive,
            flags,
        )

        with os.fdopen(fd, "rb") as origin:
            copy_fd = os.open(
                staged_archive,
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL,
                0o600,
            )

            with os.fdopen(
                copy_fd,
                "wb",
            ) as copy:
                shutil.copyfileobj(
                    origin,
                    copy,
                    1024 * 1024,
                )

        names = validate_restore_target(
            staged_archive,
            source_project,
            target_project,
        )

        members = _staged_members(
            staged_archive,
            stage,
        )

        # Repeat the target check immediately before creation.
        if (
            check_target(
                source_project,
                target_project,
            )
            != names
        ):
            raise RuntimeError(
                "Restore target changed during staging"
            )

        token = uuid.uuid4().hex
        owned = []

        try:
            for name, short in zip(
                names,
                VOLUMES,
            ):
                try:
                    _create_volume(
                        name,
                        short,
                        target_project,
                        token,
                    )

                except BaseException:
                    if _owner(name, token):
                        owned.append(name)
                    raise

                owned.append(name)

            for name, short in zip(
                names,
                VOLUMES,
            ):
                if not _owner(name, token):
                    raise RuntimeError(
                        "Restore target identity changed"
                    )

                _run_writer(
                    name,
                    image,
                    members[short],
                )

                if not _owner(name, token):
                    raise RuntimeError(
                        "Restore target identity changed"
                    )

                recovered = (
                    stage
                    / (short + ".verified.tar")
                )

                read_volume(
                    name,
                    image,
                    recovered,
                )

                check_inner_tar(
                    recovered
                )

                if (
                    file_digest(recovered)
                    != file_digest(
                        members[short]
                    )
                ):
                    raise RuntimeError(
                        "Restored volume differs from backup"
                    )

            return names

        except BaseException:
            failed = []

            for name in reversed(owned):
                if not _owner(name, token):
                    failed.append(name)
                    continue

                try:
                    _docker(
                        "volume",
                        "rm",
                        name,
                    )

                except RuntimeError:
                    failed.append(name)

            if failed:
                raise RuntimeError(
                    "Restore failed; cleanup incomplete for "
                    + ", ".join(failed)
                ) from None

            raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--archive",
        required=True,
        type=Path,
    )

    parser.add_argument(
        "--source-project",
        required=True,
    )

    parser.add_argument(
        "--target-project",
        required=True,
    )

    parser.add_argument(
        "--image",
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
        names = restore(
            args.archive,
            args.source_project,
            args.target_project,
            args.image,
        )

    except (
        OSError,
        ValueError,
        RuntimeError,
    ) as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: restored {len(names)} "
        "isolated Caddy Docker volumes"
    )

    print(
        "INFO: file backup not restored; "
        "this is not a complete system recovery"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
