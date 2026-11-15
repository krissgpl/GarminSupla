"""Read-only verification of a GarminSupla backup set.

Verifies a private manifest and both existing archive formats.
Does not prove offline consistency, authenticate the manifest,
extract files, contact Docker, or restore volumes.
"""

import argparse
import hashlib
import json
import os
import re
import stat
import sys

from datetime import datetime, timedelta
from pathlib import Path

from scripts.verify_file_backup import (
    verify_archive as verify_files,
)
from scripts.verify_caddy_volume_backup import (
    verify_archive as verify_volumes,
)


MAX_MANIFEST = 128 * 1024
CHUNK = 1024 * 1024

READ_FLAGS = (
    os.O_RDONLY
    | os.O_NOFOLLOW
    | getattr(os, "O_NONBLOCK", 0)
)

DIR_FLAGS = (
    os.O_RDONLY
    | os.O_DIRECTORY
    | os.O_NOFOLLOW
)


def _signature(info):
    return (
        info.st_dev,
        info.st_ino,
        info.st_uid,
        info.st_mode,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _private_regular(info, label):
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_uid != os.geteuid()
        or stat.S_IMODE(info.st_mode) & 0o077
    ):
        raise ValueError(
            f"{label} must be a regular owner-only file"
        )


def _unique_pairs(pairs):
    result = {}

    for key, value in pairs:
        if key in result:
            raise ValueError(
                "Duplicate backup set JSON field"
            )

        result[key] = value

    return result


def _check_schema(data, manifest_name):
    expected = {
        "format",
        "set_id",
        "created_utc",
        "source_project",
        "complete_system_backup",
        "offline_consistency_proven",
        "archives",
    }

    if (
        not isinstance(data, dict)
        or set(data) != expected
    ):
        raise ValueError(
            "Invalid backup set manifest fields"
        )

    if (
        data["format"]
        != "garminsupla-backup-set/v1"
    ):
        raise ValueError(
            "Invalid backup set manifest format"
        )

    if (
        not isinstance(data["set_id"], str)
        or re.fullmatch(
            r"[0-9a-f]{32}",
            data["set_id"],
        ) is None
    ):
        raise ValueError(
            "Invalid backup set identifier"
        )

    project = data["source_project"]

    if (
        not isinstance(project, str)
        or re.fullmatch(
            r"[a-z][a-z0-9_-]*",
            project,
        ) is None
    ):
        raise ValueError(
            "Invalid source Docker project"
        )

    if (
        data["complete_system_backup"] is not False
        or data["offline_consistency_proven"] is not False
    ):
        raise ValueError(
            "Unproven backup completeness or consistency"
        )

    stamp = data["created_utc"]

    if (
        not isinstance(stamp, str)
        or len(stamp) > 40
    ):
        raise ValueError(
            "Invalid backup set timestamp"
        )

    try:
        parsed = datetime.fromisoformat(stamp)
    except ValueError as exc:
        raise ValueError(
            "Invalid backup set timestamp"
        ) from exc

    if parsed.utcoffset() != timedelta(0):
        raise ValueError(
            "Backup set timestamp must be UTC"
        )

    entries = data["archives"]

    if (
        not isinstance(entries, dict)
        or set(entries) != {
            "files",
            "caddy_volumes",
        }
    ):
        raise ValueError(
            "Expected exactly two backup archives"
        )

    used = {manifest_name}

    for kind in ("files", "caddy_volumes"):
        item = entries[kind]

        if (
            not isinstance(item, dict)
            or set(item) != {
                "name",
                "size",
                "sha256",
            }
        ):
            raise ValueError(
                "Invalid backup set archive record"
            )

        name = item["name"]

        if (
            not isinstance(name, str)
            or re.fullmatch(
                r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}",
                name,
            ) is None
            or name in used
        ):
            raise ValueError(
                "Unsafe or duplicate archive filename"
            )

        used.add(name)

        if (
            type(item["size"]) is not int
            or item["size"] < 0
        ):
            raise ValueError(
                "Invalid backup set archive size"
            )

        digest = item["sha256"]

        if (
            not isinstance(digest, str)
            or re.fullmatch(
                r"[0-9a-f]{64}",
                digest,
            ) is None
        ):
            raise ValueError(
                "Invalid backup set archive SHA-256"
            )

    return project, entries


def _verify_entry(
    directory_fd,
    directory,
    record,
    kind,
    project,
):
    name = record["name"]
    path = directory / name

    fd = os.open(
        name,
        READ_FLAGS,
        dir_fd=directory_fd,
    )

    with os.fdopen(fd, "rb") as source:
        before = os.fstat(
            source.fileno()
        )

        _private_regular(
            before,
            "Backup archive",
        )

        if before.st_size != record["size"]:
            raise ValueError(
                "Backup set archive size mismatch"
            )

        digest = hashlib.sha256()

        while True:
            chunk = source.read(CHUNK)

            if not chunk:
                break

            digest.update(chunk)

        if (
            digest.hexdigest() != record["sha256"]
            or _signature(
                os.fstat(source.fileno())
            ) != _signature(before)
            or _signature(
                path.lstat()
            ) != _signature(before)
        ):
            raise ValueError(
                "Backup set archive SHA-256 "
                "or identity mismatch"
            )

        if kind == "files":
            count = verify_files(path)
        else:
            count = verify_volumes(
                path,
                project,
            )

        if (
            _signature(
                os.fstat(source.fileno())
            ) != _signature(before)
            or _signature(
                path.lstat()
            ) != _signature(before)
        ):
            raise ValueError(
                "Backup archive changed during verification"
            )

        return count


def verify_set(
    manifest_path: Path,
) -> tuple[int, int]:
    """Verify both referenced archives without writing files."""

    manifest_path = Path(manifest_path)

    if not manifest_path.is_absolute():
        raise ValueError(
            "Backup set manifest path must be absolute"
        )

    directory = manifest_path.parent
    info = directory.lstat()

    if (
        not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.geteuid()
        or stat.S_IMODE(info.st_mode) != 0o700
        or directory.resolve(strict=True) != directory
    ):
        raise ValueError(
            "Backup set directory must be real, "
            "owner-only 0700"
        )

    directory_fd = os.open(
        directory,
        DIR_FLAGS,
    )

    try:
        if (
            _signature(
                os.fstat(directory_fd)
            ) != _signature(info)
        ):
            raise ValueError(
                "Backup set directory changed"
            )

        fd = os.open(
            manifest_path.name,
            READ_FLAGS,
            dir_fd=directory_fd,
        )

        with os.fdopen(fd, "rb") as source:
            before = os.fstat(
                source.fileno()
            )

            _private_regular(
                before,
                "Backup set manifest",
            )

            if before.st_size > MAX_MANIFEST:
                raise ValueError(
                    "Oversized backup set manifest"
                )

            raw = source.read(
                MAX_MANIFEST + 1
            )

            if (
                len(raw) != before.st_size
                or _signature(
                    os.fstat(source.fileno())
                ) != _signature(before)
                or _signature(
                    manifest_path.lstat()
                ) != _signature(before)
            ):
                raise ValueError(
                    "Backup set manifest changed"
                )

            try:
                data = json.loads(
                    raw,
                    object_pairs_hook=_unique_pairs,
                )
            except (ValueError, UnicodeError) as exc:
                raise ValueError(
                    "Invalid backup set JSON"
                ) from exc

            project, entries = _check_schema(
                data,
                manifest_path.name,
            )

            files = _verify_entry(
                directory_fd,
                directory,
                entries["files"],
                "files",
                project,
            )

            volumes = _verify_entry(
                directory_fd,
                directory,
                entries["caddy_volumes"],
                "caddy_volumes",
                project,
            )

            if (
                _signature(
                    os.fstat(source.fileno())
                ) != _signature(before)
                or _signature(
                    manifest_path.lstat()
                ) != _signature(before)
                or _signature(
                    os.fstat(directory_fd)
                ) != _signature(info)
                or _signature(
                    directory.lstat()
                ) != _signature(info)
            ):
                raise ValueError(
                    "Backup set changed during verification"
                )

            return files, volumes

    finally:
        os.close(directory_fd)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
    )

    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    try:
        files, volumes = verify_set(
            args.manifest
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
        f"OK: verified backup set: {files} files "
        f"and {volumes} Caddy volumes"
    )
    print(
        "INFO: read-only; archive pairing does not "
        "prove offline consistency"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
