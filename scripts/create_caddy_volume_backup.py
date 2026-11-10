"""Offline-only Caddy Docker volume archive (file backup is separate).

Requires Docker, stopped Compose services, and a locally cached Python image.
"""

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from scripts.check_caddy_volumes import VOLUMES, validate
from scripts.create_backup import check_destination


VOLUME_READER = r'''
import os
import stat
import sys
import tarfile
from pathlib import Path

root = Path("/source")


def fail(error):
    raise error


with tarfile.open(
    fileobj=sys.stdout.buffer,
    mode="w|",
) as archive:

    for directory, dirs, files in os.walk(
        root,
        followlinks=False,
        onerror=fail,
    ):
        parent = Path(directory)
        dirs.sort()
        files.sort()

        for name in dirs + files:
            path = parent / name
            info = path.lstat()
            arcname = path.relative_to(
                root
            ).as_posix()

            if stat.S_ISDIR(info.st_mode):
                item = tarfile.TarInfo(
                    arcname + "/"
                )

                item.type = tarfile.DIRTYPE
                item.mode = stat.S_IMODE(
                    info.st_mode
                )
                item.uid = info.st_uid
                item.gid = info.st_gid

                archive.addfile(item)

            elif stat.S_ISREG(info.st_mode):
                flags = (
                    os.O_RDONLY
                    | os.O_NOFOLLOW
                    | os.O_NONBLOCK
                )

                fd = os.open(path, flags)

                with os.fdopen(
                    fd,
                    "rb",
                ) as source:
                    before = os.fstat(
                        source.fileno()
                    )

                    if not stat.S_ISREG(
                        before.st_mode
                    ):
                        raise RuntimeError(
                            "Non-regular volume source"
                        )

                    item = tarfile.TarInfo(
                        arcname
                    )

                    item.size = before.st_size
                    item.mode = stat.S_IMODE(
                        before.st_mode
                    )
                    item.uid = before.st_uid
                    item.gid = before.st_gid

                    archive.addfile(
                        item,
                        source,
                    )

                    after = os.fstat(
                        source.fileno()
                    )

                    if (
                        before.st_size,
                        before.st_mtime_ns,
                        before.st_ctime_ns,
                    ) != (
                        after.st_size,
                        after.st_mtime_ns,
                        after.st_ctime_ns,
                    ):
                        raise RuntimeError(
                            "Volume file changed during read"
                        )

            else:
                raise RuntimeError(
                    "Unsafe volume entry type"
                )
'''


def read_volume(
    volume: str,
    image: str,
    destination: Path,
) -> None:
    """Stream a readonly Docker volume into a private TAR file."""

    container_name = (
        f"gs-caddy-archive-{uuid.uuid4().hex}"
    )

    command = [
        "docker",
        "run",
        "--rm",
        "--name",
        container_name,
        "--pull",
        "never",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
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
            "target=/source,readonly,volume-nocopy"
        ),
        "--entrypoint",
        "python",
        image,
        "-B",
        "-S",
        "-c",
        VOLUME_READER,
    ]

    try:
        with destination.open("wb") as output:
            result = subprocess.run(
                command,
                stdout=output,
                stderr=subprocess.PIPE,
                timeout=300,
                check=False,
            )

            output.flush()
            os.fsync(
                output.fileno()
            )

    except subprocess.TimeoutExpired as exc:
        try:
            subprocess.run(
                [
                    "docker",
                    "rm",
                    "-f",
                    container_name,
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
            "Caddy volume reader timed out"
        ) from exc

    except OSError as exc:
        raise RuntimeError(
            "Caddy volume reader unavailable"
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            "Caddy volume reader failed"
        )


def check_inner_tar(
    path: Path,
) -> None:
    """Reject links, special entries, duplicates and traversal."""

    seen = set()

    try:
        with tarfile.open(
            path,
            mode="r:",
        ) as archive:

            for member in archive:
                name = member.name.rstrip("/")
                parts = name.split("/")

                if (
                    not name
                    or name.startswith("/")
                    or any(
                        part in ("", ".", "..")
                        for part in parts
                    )
                    or name in seen
                    or not (
                        member.isfile()
                        or member.isdir()
                    )
                ):
                    raise ValueError(
                        "Unsafe Caddy volume archive entry"
                    )

                seen.add(name)

    except (
        tarfile.TarError,
        OSError,
    ) as exc:
        raise ValueError(
            "Invalid Caddy volume TAR stream"
        ) from exc


def file_digest(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as source:
        for chunk in iter(
            lambda: source.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def add_file(
    archive,
    source: Path,
    name: str,
) -> None:
    info = tarfile.TarInfo(name)
    info.size = source.stat().st_size
    info.mode = 0o600
    info.uid = 0
    info.gid = 0
    info.mtime = 0

    with source.open("rb") as infile:
        archive.addfile(
            info,
            infile,
        )


def create_caddy_volume_backup(
    project: str,
    image: str,
    root: Path,
    cert_dir: Path,
    output: Path,
) -> None:
    """Publish one archive only after both volumes pass checks."""

    root, cert_dir, output = map(
        Path,
        (root, cert_dir, output),
    )

    if (
        not image
        or image.startswith("-")
    ):
        raise ValueError(
            "A locally available Docker image is required"
        )

    check_destination(
        root,
        cert_dir,
        output,
    )

    names = validate(project)

    if len(names) != len(VOLUMES):
        raise RuntimeError(
            "Unexpected Caddy volume count"
        )

    temporary_paths = []

    try:
        fd, outer_name = tempfile.mkstemp(
            prefix=".garminsupla-caddy-",
            suffix=".partial",
            dir=output.parent,
        )

        temporary_paths.append(
            Path(outer_name)
        )

        with os.fdopen(
            fd,
            "wb",
        ) as destination:

            manifest_entries = []

            with tarfile.open(
                fileobj=destination,
                mode="w:gz",
            ) as archive:

                for volume, short_name in zip(
                    names,
                    VOLUMES,
                ):
                    fd, inner_name = tempfile.mkstemp(
                        prefix=".garminsupla-volume-",
                        suffix=".tar",
                        dir=output.parent,
                    )

                    os.close(fd)

                    inner_path = Path(
                        inner_name
                    )

                    temporary_paths.append(
                        inner_path
                    )

                    read_volume(
                        volume,
                        image,
                        inner_path,
                    )

                    check_inner_tar(
                        inner_path
                    )

                    member = (
                        f"volumes/{short_name}.tar"
                    )

                    manifest_entries.append({
                        "volume": volume,
                        "member": member,
                        "size": inner_path.stat().st_size,
                        "sha256": file_digest(
                            inner_path
                        ),
                    })

                    add_file(
                        archive,
                        inner_path,
                        member,
                    )

                    inner_path.unlink()

                    temporary_paths.remove(
                        inner_path
                    )

                if validate(project) != names:
                    raise RuntimeError(
                        "Caddy volume identity changed"
                    )

                manifest = {
                    "format": "garminsupla-caddy-volumes/v1",
                    "created_utc": datetime.now(
                        timezone.utc
                    ).isoformat(),
                    "complete_system_backup": False,
                    "volumes": manifest_entries,
                }

                content = json.dumps(
                    manifest,
                    indent=2,
                ).encode("utf-8")

                info = tarfile.TarInfo(
                    "manifest.json"
                )

                info.size = len(content)
                info.mode = 0o600
                info.mtime = 0

                archive.addfile(
                    info,
                    io.BytesIO(content),
                )

            destination.flush()
            os.fsync(
                destination.fileno()
            )

        os.link(
            outer_name,
            output,
        )

        directory_fd = os.open(
            output.parent,
            os.O_RDONLY | os.O_DIRECTORY,
        )

        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)

    finally:
        for name in temporary_paths:
            name.unlink(
                missing_ok=True
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
    )

    parser.add_argument(
        "--project",
        required=True,
    )

    parser.add_argument(
        "--image",
        required=True,
    )

    parser.add_argument(
        "--root",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--cert-dir",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--confirm-stopped",
        action="store_true",
    )

    args = parser.parse_args()

    if not args.confirm_stopped:
        print(
            "ERROR: --confirm-stopped is required",
            file=sys.stderr,
        )
        return 1

    try:
        create_caddy_volume_backup(
            args.project,
            args.image,
            args.root,
            args.cert_dir,
            args.output,
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
        "OK: offline Caddy volume archive created "
        "(file backup separate)"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
